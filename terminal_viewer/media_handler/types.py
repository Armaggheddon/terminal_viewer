from typing import Protocol
from enum import Enum

import numpy as np

class UnsupportedMediaError(Exception):
    """
    UnsupportedMediaError is raised when the media type is not supported
    """
    pass

class EndMediaError(Exception):
    """ EndMediaError is raised when the media has ended """
    pass


class MediaType(Enum):
    UNSUPPORTED_MEDIA = 0
    IMAGE = 1
    VIDEO = 2

class MediaCommand(Enum):
    NOOP = 1
    SKIP_FRAME = 2
    PREV_FRAME = 3
    PLAY_PAUSE = 4
    REWIND = 5


class MediaDigest(Protocol):
    """
    MediaDigest is an interface for media handlers
    """
    def next_frame(self) -> np.ndarray:
        """
        Get the next frame of the media
        """
        ...

