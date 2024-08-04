from typing import Union

import cv2
import numpy as np

from .video_digest import VideoDigest
from .image_digest import ImageDigest
from .unsupported_digest import UnsupportedDigest
from .types import MediaType, MediaCommand

def get_media_type(media_path: str) -> MediaType:
    """
    Get the media type of the media file
    """
    if cv2.haveImageReader(media_path):
        return MediaType.IMAGE
    try:
        cap = cv2.VideoCapture(media_path)

        if cap.isOpened():
            # Cap is opened if the media is a video
            # but could also open audio files (why?)
            # so check if the frame width and height are not 0
            fw = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            fh = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            cap.release()
            if fw == 0 or fh == 0:
                return MediaType.UNSUPPORTED_MEDIA

            return MediaType.VIDEO
    except Exception:
        return MediaType.UNSUPPORTED_MEDIA
    
class MediaHandler():
    """
    MediaHandler is a class that handles media media digests
    and abstracts the specific digest type from the caller
    """
    def __init__(self, media_path: str) -> None:
        self.media_path = media_path
        media_type = get_media_type(media_path)
        self.is_video = media_type == MediaType.VIDEO
        self.media_digest = self._get_media_digest(media_type, media_path)
    
    def _get_media_digest(
            self, 
            media_type: MediaType, 
            media_path: str
            ) -> Union[ImageDigest, VideoDigest, UnsupportedDigest]:
        """
        Get the media digest based on the media type
        
        Parameters:
        - media_type (MediaType): the type of the media
        - media_path (str): the path to the media file

        Returns:
        - Union[ImageDigest, VideoDigest, UnsupportedDigest]: the media digest
        """
        if media_type == MediaType.IMAGE:
            return ImageDigest(media_path)
        elif media_type == MediaType.VIDEO:
            return VideoDigest(media_path)
        else:
            return UnsupportedDigest(media_path)

    def duration(self) -> Union[int, None]:
        """
        Get the duration of the media in milliseconds
        
        Returns:
        - Union[int, None]: the duration of the media in milliseconds,
            or None if the media is not a video
        """
        if self.is_video:
            return self.media_digest.duration_ms
    
    def current_time(self) -> Union[int, None]:
        """
        Get the current time of the media in milliseconds
        
        Returns:
        - Union[int, None]: the current time of the media in milliseconds,
            or None if the media is not a video
        """
        if self.is_video:
            return self.media_digest.current_pos_ms
    
    def next_frame(self) -> np.ndarray:
        """ Get the next frame of the media """
        return self.media_digest.next_frame()
    
    def skip_frame(self) -> None:
        """ Skip a frame in the media """
        if self.is_video:
            self.media_digest.add_command(MediaCommand.SKIP_FRAME)

    def prev_frame(self) -> None:
        """ Go back a frame in the media """
        if self.is_video:
            self.media_digest.add_command(MediaCommand.PREV_FRAME)
    
    def play_pause(self) -> None:
        """ Play or pause the media based on the current state """
        if self.is_video:
            self.media_digest.add_command(MediaCommand.PLAY_PAUSE)
    
    def rewind(self) -> None:
        """ Rewind the media """
        if self.is_video:
            self.media_digest.add_command(MediaCommand.REWIND)

    def close(self) -> None:
        """ Close the media digest """
        if self.is_video:
            self.media_digest.close()