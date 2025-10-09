### 后端 API 总览（GraphQL + 少量 REST）

- **基础信息**
  - **Base URL**: 由 `API_URL` 环境变量决定（默认 `http://localhost:7263`）
  - **GraphQL 端点**: `http://localhost:7263/graphql`
```121:136:demo/backend/server/app.py
# Add GraphQL route to Flask app.
app.add_url_rule(
    "/graphql",
    view_func=MyGraphQLView.as_view(
        "graphql_view",
        schema=schema,
        allow_queries_via_get=False,
        multipart_uploads_enabled=True,
    ),
)
```

- **健康检查与静态资源**
  - `GET /healthy` → 健康检查
  - `GET /gallery/<path>` → 访问示例视频
  - `GET /uploads/<path>` → 访问上传的视频
  - `GET /posters/<path>` → 访问视频首帧海报

- **流式推理 REST 接口**
  - `POST /propagate_in_video`  
    - Body(JSON): `{ "session_id": string, "start_frame_index": number }`
    - 返回值: `multipart/x-savi-stream; boundary=frame`，连续输出 JSON 分块，内容为每帧的分割结果（RLE 掩码）
```76:88:demo/backend/server/app.py
@app.route("/propagate_in_video", methods=["POST"])
def propagate_in_video() -> Response:
    data = request.json
    args = {"session_id": data["session_id"], "start_frame_index": data.get("start_frame_index", 0)}
    boundary = "frame"
    frame = gen_track_with_mask_stream(boundary, **args)
    return Response(frame, mimetype="multipart/x-savi-stream; boundary=" + boundary)
```

### GraphQL Schema（文档即代码）

- 入口 Schema
```354:357:demo/backend/server/data/schema.py
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
)
```

- **Query**
  - **default_video**: 返回默认视频（可由 `DEFAULT_VIDEO_PATH` 指定）
  - **videos**: 返回全部可用视频列表（Relay 连接）
```60:89:demo/backend/server/data/schema.py
@strawberry.field
def default_video(self) -> Video: ...
@relay.connection(relay.ListConnection[Video])
def videos(self) -> Iterable[Video]: ...
```

- **Mutation（核心业务）**
  - **upload_video(file, start_time_sec?, duration_time_sec?) → Video**  
    上传视频，后端转码并写入 `uploads`
  - **start_session(input { path }) → { session_id }**  
    初始化推理会话（视频路径以 `DATA_PATH` 为前缀）
  - **close_session(input { session_id }) → { success }**
  - **add_points(input { session_id, frame_index, object_id, labels, points, clear_old_points }) → RLEMaskListOnFrame**  
    在指定帧添加提示点，立即返回该帧的分割结果
  - **remove_object(input { session_id, object_id }) → [RLEMaskListOnFrame]**  
    移除对象并返回受影响帧的结果
  - **clear_points_in_frame(input { session_id, frame_index, object_id }) → RLEMaskListOnFrame**
  - **clear_points_in_video(input { session_id }) → { success }**
  - **cancel_propagate_in_video(input { session_id }) → { success }**
```122:257:demo/backend/server/data/schema.py
def upload_video(... ) -> Video: ...
def start_session(... ) -> StartSession: ...
def close_session(... ) -> CloseSession: ...
def add_points(... ) -> RLEMaskListOnFrame: ...
def remove_object(... ) -> List[RLEMaskListOnFrame]: ...
def clear_points_in_frame(... ) -> RLEMaskListOnFrame: ...
def clear_points_in_video(... ) -> ClearPointsInVideo: ...
def cancel_propagate_in_video(... ) -> CancelPropagateInVideo: ...
```

- **重要类型（摘）**
  - `Video`: `code, path, poster_path, width, height`，并提供 `url, poster_url` 计算字段（由 `API_URL` 拼接）
  - `RLEMask`: `size: [H, W], counts: string, order: "F"`
  - `RLEMaskForObject`: `object_id, rle_mask`
  - `RLEMaskListOnFrame`: `frame_index, rle_mask_list`
```16:43:demo/backend/server/data/data_types.py
@strawberry.type
class Video(relay.Node): ...
@strawberry.field
def url(self) -> str: ...
@strawberry.field
def poster_url(self) -> str: ...
```

### 使用建议
- 在 `http://localhost:7263/graphql` 通过 GraphQL 工具（GraphiQL/Insomnia/Postman/Relay）进行自省与调试。
- 需要长视频自动跟踪时：先通过 GraphQL 建立会话与标注点，再调用 `POST /propagate_in_video` 获取连续帧的分割结果流。
- 前端仓库含有 SDL 参考：`demo/frontend/schemas/video-api-schema.graphql`。

下面给你一套在 Flutter 中进行 GraphQL 请求的最小闭环做法，包含查询、变更、文件上传（与你后端的 `upload_video(file: Upload, ...)` 匹配），以及常见配置要点。

### 1. 安装依赖
在 `pubspec.yaml` 中加入：
```yaml
dependencies:
  graphql_flutter: ^5.1.2
```

### 2. 初始化客户端
```dart
import 'package:flutter/widgets.dart';
import 'package:graphql_flutter/graphql_flutter.dart';

final httpLink = HttpLink(
  'http://localhost:7263/graphql', // 替换为你的后端地址
  defaultHeaders: {
    // 如果需要鉴权或携带自定义头，在此添加
    // 'Authorization': 'Bearer <token>',
  },
);

final ValueNotifier<GraphQLClient> gqlClient = ValueNotifier(
  GraphQLClient(
    link: httpLink,
    cache: GraphQLCache(store: InMemoryStore()),
  ),
);

// 在应用入口包裹
Widget buildApp(Widget app) {
  return GraphQLProvider(
    client: gqlClient,
    child: app,
  );
}
```

### 3. 发送查询（Query）
示例：获取默认视频与视频列表（对应后端 `Query.default_video`、`Query.videos`）
```dart
const String query = r'''
  query Demo {
    default_video { code path poster_path width height }
    videos(first: 20) {
      edges {
        node { code path width height }
      }
    }
  }
''';

final QueryOptions options = QueryOptions(
  document: gql(query),
);

final result = await gqlClient.value.query(options);
if (result.hasException) {
  print(result.exception.toString());
} else {
  print(result.data);
}
```

### 4. 发送变更（Mutation）
示例：开启会话（对应 `start_session`）
```dart
const String mutation = r'''
  mutation StartSession($path: String!) {
    start_session(input: { path: $path }) {
      session_id
    }
  }
''';

final result = await gqlClient.value.mutate(
  MutationOptions(
    document: gql(mutation),
    variables: { 'path': 'gallery/05_default_juggle.mp4' }, // 你的相对路径
  ),
);
if (result.hasException) {
  print(result.exception.toString());
} else {
  final sessionId = result.data?['start_session']['session_id'];
  print(sessionId);
}
```

示例：添加点提示（对应 `add_points`）
```dart
const String mutation = r'''
  mutation AddPoints($input: AddPointsInput!) {
    add_points(input: $input) {
      frame_index
      rle_mask_list {
        object_id
        rle_mask { size counts order }
      }
    }
  }
''';

final result = await gqlClient.value.mutate(
  MutationOptions(
    document: gql(mutation),
    variables: {
      'input': {
        'session_id': '<your-session-id>',
        'frame_index': 0,
        'object_id': 1,
        'labels': [1, 1],
        'points': [[100.0, 120.0], [140.0, 160.0]],
        'clear_old_points': false,
      }
    },
  ),
);
```

### 5. 文件上传（匹配 `upload_video(file: Upload, ...)`）
`graphql_flutter` 对变量中含 `http.MultipartFile` 会自动按 GraphQL Multipart Request 规范发送。
```dart
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:path/path.dart' as p;
import 'package:graphql_flutter/graphql_flutter.dart';

const String uploadMutation = r'''
  mutation UploadVideo($file: Upload!, $start: Float, $duration: Float) {
    upload_video(file: $file, start_time_sec: $start, duration_time_sec: $duration) {
      code path poster_path width height
    }
  }
''';

Future<void> uploadVideo(File file) async {
  final bytes = await file.readAsBytes();
  final multipart = http.MultipartFile.fromBytes(
    'file',
    bytes,
    filename: p.basename(file.path),
    contentType: MediaType('video', 'mp4'), // 需要导入 `package:http_parser/http_parser.dart`
  );

  final result = await gqlClient.value.mutate(
    MutationOptions(
      document: gql(uploadMutation),
      variables: {
        'file': multipart,
        'start': 0.0,
        'duration': 10.0,
      },
    ),
  );

  if (result.hasException) {
    print(result.exception.toString());
  } else {
    print(result.data);
  }
}
```

依赖补充（`MediaType`）：
```yaml
dependencies:
  http_parser: ^4.0.2
```

### 6. 会话相关常用变更对应关系
- 开启会话：`start_session(input { path }) → { session_id }`
- 关闭会话：`close_session(input { session_id }) → { success }`
- 添加点：`add_points(input { session_id, frame_index, object_id, labels, points, clear_old_points })`
- 清空帧点：`clear_points_in_frame(input { ... })`
- 清空全视频点：`clear_points_in_video(input { session_id })`
- 删除对象：`remove_object(input { session_id, object_id })`
- 取消传播：`cancel_propagate_in_video(input { session_id })`

### 7. 调试与错误处理
- `result.hasException` 为 true 时检查 `result.exception.graphqlErrors` 与 `linkException`。
- 后端关闭 GET 查询：务必使用 POST（`graphql_flutter` 默认就是 POST）。
- 若需鉴权或 Cookie，会在 `HttpLink.defaultHeaders` 中添加相应头；如需携带 Cookie，可将同域或在自定义 `HttpClient` 层处理。

### 8. 流式跟踪说明
持续帧结果的流式返回不是 GraphQL，而是 REST：`POST /propagate_in_video`，返回 `multipart/x-savi-stream`。Flutter 可用 `http.Client().send()` 读取字节流并按 `\r\n` 边界解析。这部分如需要我可以给你最小解析实现。

小结
- 使用 `graphql_flutter` 建立 `HttpLink`，通过 `query/mutate` 完成查询与变更。
- 文件上传用 `http.MultipartFile` 放入变量，库会自动用 GraphQL multipart 规范发送。
- 流式传播不是 GraphQL，而是 REST 流式接口，需单独处理字节流。