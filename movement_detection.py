import cv2
import numpy as np


class MotionDetector:
    """
    This class provides a simple motion detection mechanism using computer vision techniques.

    Attributes:
        previous_frame (numpy.ndarray): The previous processed frame used as a reference for motion detection.

    Methods:
        __init__(): Initializes the MotionDetector instance.
        detect_motion(current_frame, threshold=25): Detects motion between the current frame and the previous frame.
        initialize_frame(frame): Preprocesses the input frame for motion detection.
    """

    def __init__(self):

        """
        Initializes the MotionDetector instance by setting the initial previous_frame to None.
        """

        self.previous_frame = None

    def detect_motion(self, current_frame, threshold=25):

        """
        Detects motion between the current frame and the previous frame.

        Args:
            current_frame (numpy.ndarray): The current frame captured from a video feed.
            threshold (int): The threshold value for motion detection. Pixels with differences above this value are considered as motion.

        Returns:
            bool: True if motion is detected, False otherwise.
        """

        try:
            if self.previous_frame is None:
                self.previous_frame = self.initialize_frame(current_frame)

            current_frame = self.initialize_frame(current_frame)
            frame_delta = cv2.absdiff(self.previous_frame, current_frame)
            _, thresh = cv2.threshold(frame_delta, threshold, 255, cv2.THRESH_BINARY)

            self.previous_frame = current_frame
            return np.sum(thresh) > 0

        except Exception as e:
            print(f'Error during motion detection: {e}')
            return False

    @staticmethod
    def initialize_frame(frame):
        """
        Preprocesses the input frame for motion detection.

        Args:
            frame (numpy.ndarray): The frame to be preprocessed.

        Returns:
            numpy.ndarray: The preprocessed frame.
        """

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur_frame = cv2.GaussianBlur(gray_frame, (21, 21), 0)
        return blur_frame
