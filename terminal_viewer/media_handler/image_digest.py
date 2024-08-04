import cv2
import numpy as np

from .types import MediaDigest


class ImageDigest(MediaDigest):
    """
    ImageDigest is a class that handles image media
    """
    
    def __init__(self, media_path: str) -> None:
        self.media_path = media_path
        self.img = cv2.imread(self.media_path)

    def next_frame(self) -> np.ndarray:
        """
        Image has only one frame so just return the image
        """
        return self.img