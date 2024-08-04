import cv2
import numpy as np

from .types import EndMediaError, MediaCommand, MediaDigest

class VideoDigest(MediaDigest):
    """
    VideoDigest is a class that handles video media
    """
    def __init__(self, media_path: str) -> None:
        self.media_path = media_path

        self.cap = cv2.VideoCapture(self.media_path)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.duration_ms = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)/self.fps * 1000
        self.current_pos_ms = 0.0
        self.is_playing = True
        self.command_queue = []
        self.last_frame = None

        # All commands return a boolean to indicate if 
        # the next frame should be sampled. For example,
        # if the video is paused, the next frame should NOT be
        # sampled, but if the video is playing, the next frame
        # should be sampled
        self.command_map = {
            MediaCommand.SKIP_FRAME: self._skip_frame,
            MediaCommand.PREV_FRAME: self._prev_frame,
            MediaCommand.REWIND: self._rewind,
            MediaCommand.PLAY_PAUSE: self._play_pause
        }

    def add_command(self, command: MediaCommand) -> None:
        self.command_queue.append(command)

    def next_frame(self) -> np.ndarray:
        """
        Get the next frame of the video based on the current state
        and the commands in the command queue
        """

        should_sample = False
        if self.command_queue:
            command = self.command_queue.pop(0)
            should_sample = self.command_map[command]()

        if not self.is_playing and not should_sample:
            return self.last_frame

        ret, frame = self.cap.read()
        self.last_frame = frame
        # get current time of frame
        self.current_pos_ms = self.cap.get(cv2.CAP_PROP_POS_MSEC)
        if not ret:
            raise EndMediaError("End of video reached")
        return self.last_frame
    
    def _skip_frame(self) -> bool:
        curr_frame_num = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
        if curr_frame_num + 1 < self.cap.get(cv2.CAP_PROP_FRAME_COUNT):
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, curr_frame_num + 1)
        return True

    def _prev_frame(self) -> bool:
        pos = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
        if pos > 0:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, pos-2)
        return True
    
    def _rewind(self) -> bool:
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        # set playing to True
        self.is_playing = True
        return True
    
    def _play_pause(self) -> bool:
        self.is_playing = not self.is_playing
        return False
    
    def close(self):
        """ Close the video capture and release the resources"""
        if self.cap:
            self.cap.release()
        