import av
import av.error
import av.video
import av.video.format
import av.video.reformatter
import numpy as np

from .types import EndMediaError, MediaCommand, MediaDigest

class VideoDigest(MediaDigest):
    """
    VideoDigest is a class that handles video media
    """
    def __init__(self, media_path: str) -> None:
        self.media_path = media_path
        
        self.video_container = av.open(self.media_path)
        self.time_base = self.video_container.streams.video[0].time_base
        self.average_rate = self.video_container.streams.video[0].average_rate
        self.duration_ms = int(self.video_container.duration / 1000)
        self.current_pos_ms = 0

        # self.cap = cv2.VideoCapture(self.media_path)
        # self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        # self.duration_ms = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)/self.fps * 1000
        # self.current_pos_ms = 0.0
        self.is_playing = True
        self.command_queue = []
        self.last_frame = None

        self.first_keyframe_ms = None

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

        try:
            frame = next(self.video_container.decode(video=0))
            if self.first_keyframe_ms is None and frame.key_frame:
                self.first_keyframe_ms = int(frame.time * 1000) # convert to milliseconds
            self.last_frame = frame.to_rgb().to_ndarray()[:, :, ::-1] # convert to BGR
            # get current time of frame in ms
            self.current_pos_ms = int(frame.time * 1000)
        except StopIteration:
                raise EndMediaError("End of video reached")
        except av.error.EOFError:
            raise EndMediaError("End of video reached")
        
        return self.last_frame
    
    def _skip_frame(self) -> bool:
        """ Skip to the next key frame """
        self.video_container.seek(self.current_pos_ms * 1000, backward=False)
        return True

    def _prev_frame(self) -> bool:
        """ Seek to the previous key frame """
        # sample_time = -1
        sample_time = (self.current_pos_ms-1000) * 1000
        if self.first_keyframe_ms is None:
            sample_time = -1
        
        try:
            self.video_container.seek(sample_time, backward=True, any_frame=False)
        except:
            self.video_container.seek(-1, backward=True, any_frame=True)
        return True

    def _rewind(self) -> bool:
        self.video_container.seek(-1, backward=True, any_frame=True)
        self.is_playing = True
        return True
    
    def _play_pause(self) -> bool:
        self.is_playing = not self.is_playing
        return False
    
    def close(self):
        """ Close the video capture and release the resources"""
        self.video_container.close()
        