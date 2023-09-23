import os
import cv2
from datetime import datetime


class VideoSaver:
    """
    This class facilitates the process of saving a sequence of frames as a video clip.

    Attributes:
        video_name (str): The name of the output video file.
        video_frames (list): List of frames to be saved as a video.

    Methods:
        __init__(): Initializes the VideoSaver instance.
        save_video_clip(video_frames=None): Saves the frames as a video clip.
        set_video_name(name=None): Sets the video name based on the provided name or a timestamp.
        set_video_frames(frames): Sets the frames to be saved in the video.
        get_current_time(): A static method that gets the current time and returns it in the specified format.
    """

    def __init__(self):

        """
        Initializes the VideoSaver instance with default values.
        """

        self.video_name = None
        self.video_frames = []

    def save_video_clip(self, video_frames=None):

        """
        Saves the frames as a video clip with the given frames or the frames previously set.

        Args:
            video_frames (list, optional): List of frames to be saved. If not provided, uses the frames previously set.

        Raises:
            ValueError: If no frames are provided or available.
        """

        print("Saving video clip...")
        try:
            self.set_video_name()
            self.set_video_frames(video_frames)

            if not self.video_frames:
                raise ValueError("No frames to save.")

            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            output_file_path = os.path.join('data/videos', f'{self.video_name}.avi')
            out = cv2.VideoWriter(output_file_path, fourcc, 10, (640, 480))

            for frame in self.video_frames:
                out.write(frame)

            print(f"Video saved successfully at {output_file_path}")
            out.release()
            self.video_name = None
            self.video_frames.clear()

        except Exception as e:
            print(f"Error while saving video: {e}")

    def set_video_name(self, name=None):

        """
        Sets the name of the video based on the provided name or a timestamp.

        Args:
            name (str, optional): The desired name for the video.

        """

        try:
            self.video_name = name or f'unidentified_video_{self.get_current_time()}'
        except Exception as e:
            print(f'Error while setting video name: {e}')

    def set_video_frames(self, frames):

        """
        Sets the frames to be saved in the video.

        Args:
            frames (list): List of frames to be saved in the video.

        Raises:
            ValueError: If no frames are provided.
        """

        try:
            if frames is None:
                raise ValueError('No frames provided.')

            self.video_frames = frames

        except Exception as e:
            print(f'Error while setting video frames: {e}')

    @staticmethod
    def get_current_time():

        """
        Gets the current time and returns it in the specified format.

        Returns:
            str: Current time in the format "YYYY-MM-DD_HH-MM-SS".
        """

        return datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
