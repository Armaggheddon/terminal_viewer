import numpy as np

from .types import MediaDigest, UnsupportedMediaError

class UnsupportedDigest(MediaDigest):
    """
    UnsupportedDigest is a class that handles unsupported media. 
    It raises an UnsupportedMediaError when next_frame is called
    so that callers dont have to have special logic for unsupported media
    """
    def __init__(self, media_path: str) -> None:
        
        self.media_path = media_path

    def next_frame(self) -> np.ndarray:
        """
        Raise an UnsupportedMediaError when next_frame is called
        since unsupported media has no frames
        """
        raise UnsupportedMediaError()