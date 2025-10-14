# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

import os
import shutil
import subprocess
from glob import glob
from pathlib import Path
from typing import Dict, Optional

import imagesize
from app_conf import GALLERY_PATH, POSTERS_PATH, POSTERS_PREFIX
from data.transcoder import get_video_metadata
from data.data_types import Video
from tqdm import tqdm


def preload_data() -> Dict[str, Video]:
    """
    Preload data including gallery videos and their posters.
    """
    # Dictionaries for videos and datasets on the backend.
    # Note that since Python 3.7, dictionaries preserve their insert order, so
    # when looping over its `.values()`, elements inserted first also appear first.
    # https://stackoverflow.com/questions/39980323/are-dictionaries-ordered-in-python-3-6
    all_videos = {}

    video_path_pattern = os.path.join(GALLERY_PATH, "**/*.mp4")
    video_paths = glob(video_path_pattern, recursive=True)

    for p in tqdm(video_paths):
        video = get_video(p, GALLERY_PATH)
        all_videos[video.code] = video

    return all_videos


def get_video(
    filepath: os.PathLike,
    absolute_path: Path,
    file_key: Optional[str] = None,
    generate_poster: bool = True,
    width: Optional[int] = None,
    height: Optional[int] = None,
    fps: Optional[float] = None,
    duration_sec: Optional[float] = None,
    num_video_frames: Optional[int] = None,
    verbose: Optional[bool] = False,
) -> Video:
    """
    Get video object given
    """
    # Use absolute_path to include the parent directory in the video
    video_path = os.path.relpath(filepath, absolute_path.parent)
    poster_path = None
    if generate_poster:
        poster_id = os.path.splitext(os.path.basename(filepath))[0]
        poster_filename = f"{str(poster_id)}.jpg"
        poster_path = f"{POSTERS_PREFIX}/{poster_filename}"

        # Extract the first frame from video
        poster_output_path = os.path.join(POSTERS_PATH, poster_filename)
        ffmpeg = shutil.which("ffmpeg")
        subprocess.call(
            [
                ffmpeg,
                "-y",
                "-i",
                str(filepath),
                "-pix_fmt",
                "yuv420p",
                "-frames:v",
                "1",
                "-update",
                "1",
                "-strict",
                "unofficial",
                str(poster_output_path),
            ],
            stdout=None if verbose else subprocess.DEVNULL,
            stderr=None if verbose else subprocess.DEVNULL,
        )

        # Extract video width and height from poster. This is important to optimize
        # rendering previews in the mosaic video preview.
        width, height = imagesize.get(poster_output_path)

    # 如果仍有缺失的元数据，使用解封装读取视频元信息进行补齐
    if (
        fps is None
        or duration_sec is None
        or width is None
        or height is None
        or num_video_frames is None
    ):
        try:
            md = get_video_metadata(str(filepath))
            if fps is None:
                fps = md.fps
            if duration_sec is None:
                duration_sec = md.duration_sec
            if width is None:
                width = md.width
            if height is None:
                height = md.height
            if num_video_frames is None:
                num_video_frames = md.num_video_frames
        except Exception:
            pass

    return Video(
        code=video_path,
        path=video_path if file_key is None else file_key,
        poster_path=poster_path,
        width=width,
        height=height,
        fps=fps,
        duration_sec=duration_sec,
        num_video_frames=num_video_frames,
    )
