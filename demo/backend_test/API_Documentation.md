# SAM2 GraphQL API 文档

## 概述
本文档描述了运行在 `http://10.102.64.48:7263/graphql` 的SAM2 GraphQL API的所有可用接口。

## 基础信息
- **端点**: `http://10.102.64.48:7263/graphql`
- **接口类型**: GraphQL
- **框架**: Strawberry GraphQL

## Query（查询）接口

### 1. defaultVideo
获取默认视频信息
```graphql
query GetDefaultVideo {
  defaultVideo {
    id
    path
    posterPath
    width
    height
    url
    posterUrl
  }
}
```

**返回类型**: `Video!`

### 2. videos
获取视频列表（支持分页）
```graphql
query GetVideos($first: Int, $after: String, $last: Int, $before: String) {
  videos(first: $first, after: $after, last: $last, before: $before) {
    edges {
      node {
        id
        path
        posterPath
        width
        height
        url
        posterUrl
      }
    }
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
    }
  }
}
```

**参数**:
- `before`: String (可选) - 分页游标
- `after`: String (可选) - 分页游标
- `first`: Int (可选) - 获取前N条记录
- `last`: Int (可选) - 获取后N条记录

**返回类型**: `VideoConnection!`

## Mutation（变更）接口

### 1. uploadVideo
上传视频文件
```graphql
mutation UploadVideo($file: Upload!, $startTimeSec: Float, $durationTimeSec: Float) {
  uploadVideo(
    file: $file
    startTimeSec: $startTimeSec
    durationTimeSec: $durationTimeSec
  ) {
    id
    path
    posterPath
    width
    height
    url
    posterUrl
  }
}
```

**参数**:
- `file`: Upload! (必需) - 视频文件
- `startTimeSec`: Float (可选) - 开始时间（秒）
- `durationTimeSec`: Float (可选) - 持续时间（秒）

**返回类型**: `Video!`

### 2. startSession
开始SAM2处理会话
```graphql
mutation StartSession($input: StartSessionInput!) {
  startSession(input: $input) {
    # 返回类型待确认
  }
}
```

**参数**:
- `input`: StartSessionInput! (必需) - 会话配置

**返回类型**: `StartSession!`

### 3. closeSession
关闭SAM2处理会话
```graphql
mutation CloseSession($input: CloseSessionInput!) {
  closeSession(input: $input) {
    # 返回类型待确认
  }
}
```

**参数**:
- `input`: CloseSessionInput! (必需) - 会话关闭配置

**返回类型**: `CloseSession!`

### 4. addPoints
添加交互点进行分割
```graphql
mutation AddPoints($input: AddPointsInput!) {
  addPoints(input: $input) {
    # 返回RLE格式的掩码列表
  }
}
```

**参数**:
- `input`: AddPointsInput! (必需) - 交互点配置

**返回类型**: `RLEMaskListOnFrame!`

### 5. removeObject
移除对象
```graphql
mutation RemoveObject($input: RemoveObjectInput!) {
  removeObject(input: $input) {
    # 返回更新后的掩码列表
  }
}
```

**参数**:
- `input`: RemoveObjectInput! (必需) - 对象移除配置

**返回类型**: `[RLEMaskListOnFrame!]!`

### 6. clearPointsInFrame
清除当前帧的所有交互点
```graphql
mutation ClearPointsInFrame($input: ClearPointsInFrameInput!) {
  clearPointsInFrame(input: $input) {
    # 返回更新后的掩码列表
  }
}
```

**参数**:
- `input`: ClearPointsInFrameInput! (必需) - 清除配置

**返回类型**: `RLEMaskListOnFrame!`

### 7. clearPointsInVideo
清除整个视频的所有交互点
```graphql
mutation ClearPointsInVideo($input: ClearPointsInVideoInput!) {
  clearPointsInVideo(input: $input) {
    # 返回清除结果
  }
}
```

**参数**:
- `input`: ClearPointsInVideoInput! (必需) - 清除配置

**返回类型**: `ClearPointsInVideo!`

### 8. cancelPropagateInVideo
取消视频中的传播
```graphql
mutation CancelPropagateInVideo($input: CancelPropagateInVideoInput!) {
  cancelPropagateInVideo(input: $input) {
    # 返回取消结果
  }
}
```

**参数**:
- `input`: CancelPropagateInVideoInput! (必需) - 取消配置

**返回类型**: `CancelPropagateInVideo!`

## 数据类型

### Video
视频对象
```graphql
type Video implements Node {
  id: ID!                    # 全局唯一ID
  path: String!              # 文件路径
  posterPath: String         # 海报图片路径
  width: Int!                # 视频宽度
  height: Int!               # 视频高度
  url: String!               # 视频URL
  posterUrl: String!         # 海报图片URL
}
```

### VideoConnection
视频连接类型（用于分页）
```graphql
type VideoConnection {
  edges: [VideoEdge!]!       # 视频边列表
  pageInfo: PageInfo!        # 分页信息
}
```

### VideoEdge
视频边类型
```graphql
type VideoEdge {
  node: Video!               # 视频节点
}
```

### PageInfo
分页信息
```graphql
type PageInfo {
  hasNextPage: Boolean!      # 是否有下一页
  hasPreviousPage: Boolean!   # 是否有上一页
  startCursor: String        # 开始游标
  endCursor: String          # 结束游标
}
```

### RLEMaskListOnFrame
帧上的RLE掩码列表
```graphql
type RLEMaskListOnFrame {
  # 具体字段待确认
}
```

### RLEMaskForObject
对象的RLE掩码
```graphql
type RLEMaskForObject {
  # 具体字段待确认
}
```

### RLEMask
RLE格式的掩码
```graphql
type RLEMask {
  # 具体字段待确认
}
```

## 输入类型

### StartSessionInput
开始会话的输入参数
```graphql
input StartSessionInput {
  # 具体字段待确认
}
```

### CloseSessionInput
关闭会话的输入参数
```graphql
input CloseSessionInput {
  # 具体字段待确认
}
```

### AddPointsInput
添加交互点的输入参数
```graphql
input AddPointsInput {
  # 具体字段待确认
}
```

### RemoveObjectInput
移除对象的输入参数
```graphql
input RemoveObjectInput {
  # 具体字段待确认
}
```

### ClearPointsInFrameInput
清除帧交互点的输入参数
```graphql
input ClearPointsInFrameInput {
  # 具体字段待确认
}
```

### ClearPointsInVideoInput
清除视频交互点的输入参数
```graphql
input ClearPointsInVideoInput {
  # 具体字段待确认
}
```

### CancelPropagateInVideoInput
取消视频传播的输入参数
```graphql
input CancelPropagateInVideoInput {
  # 具体字段待确认
}
```

## 标量类型

- `ID`: 全局唯一标识符
- `String`: 字符串
- `Int`: 整数
- `Float`: 浮点数
- `Boolean`: 布尔值
- `Upload`: 文件上传类型

## 使用示例

### 1. 获取默认视频
```graphql
query GetDefaultVideo {
  defaultVideo {
    id
    path
    width
    height
    url
    posterUrl
  }
}
```

**变量**: 无需变量

### 2. 上传视频
```graphql
mutation UploadVideo($file: Upload!, $startTimeSec: Float, $durationTimeSec: Float) {
  uploadVideo(
    file: $file
    startTimeSec: $startTimeSec
    durationTimeSec: $durationTimeSec
  ) {
    id
    path
    width
    height
    url
  }
}
```

**变量示例**:
```json
{
  "file": "<MultipartFile>",
  "startTimeSec": 0.0,
  "durationTimeSec": 10.0
}
```

### 3. 获取视频列表（分页）
```graphql
query GetVideos($first: Int, $after: String) {
  videos(first: $first, after: $after) {
    edges {
      node {
        id
        path
        width
        height
        url
      }
    }
    pageInfo {
      hasNextPage
      hasPreviousPage
      endCursor
    }
  }
}
```

**变量示例**:
```json
{
  "first": 10,
  "after": null
}
```

### 4. 开始会话
```graphql
mutation StartSession($input: StartSessionInput!) {
  startSession(input: $input) {
    sessionId
  }
}
```

**变量示例**:
```json
{
  "input": {
    "path": "gallery/05_default_juggle.mp4"
  }
}
```

### 5. 添加交互点
```graphql
mutation AddPoints($input: AddPointsInput!) {
  addPoints(input: $input) {
    frameIndex
    rleMaskList {
      objectId
      rleMask {
        size
        counts
        order
      }
    }
  }
}
```

**变量示例**:
```json
{
  "input": {
    "sessionId": "session_123",
    "frameIndex": 0,
    "objectId": 1,
    "labels": [1, 1],
    "points": [[100.0, 120.0], [140.0, 160.0]],
    "clearOldPoints": false
  }
}
```

## 注意事项

1. **查询命名**: 所有查询和变更都应该使用有意义的名称，便于调试和维护
2. **变量声明**: 在查询/变更中声明变量时，必须在操作中使用这些变量
3. **文件上传**: 使用 `Upload` 标量类型处理文件上传
4. **分页**: 使用基于游标的分页机制
5. **会话管理**: 需要先开始会话才能进行SAM2处理
6. **交互点**: 通过添加交互点来进行图像分割
7. **RLE掩码**: 返回的掩码使用RLE（Run-Length Encoding）格式
8. **参数传递**: 使用变量（`$variableName`）而不是在查询中直接声明参数类型

## 错误处理

GraphQL API会返回标准的GraphQL错误响应，包含：
- `message`: 错误描述
- `locations`: 错误位置
- `path`: 错误路径
- `extensions`: 扩展错误信息

## 更新日志

- 初始版本: 基于当前schema分析
- v1.1: 修正GraphQL查询格式，添加正确的变量声明和使用
- 待完善: 部分输入类型和返回类型的详细字段结构
