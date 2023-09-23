import datetime
import random
import sys
from os import walk
import cv2
import face_recognition
from movement_detection import MotionDetector
from save_video_clip import VideoSaver
from email_notification import EmailSender

PASSWORD = ''
EMAIL = ''
RECEIVER = ''
IMAGE_DIRECTORY = 'data/known_faces'
TOLERANCE = 0.6
RANDOM_FRAMES_TO_SEND = 5
RECORDING_DURATION_THRESHOLD = 120


def get_random_frames(frames, num_frames=5):
    """
    Get a random selection of frames from a list of frames.

    Args:
        frames (list): List of frames to select from.
        num_frames (int, optional): Number of frames to select (default is 5).

    Returns:
        list: Randomly selected frames.
    """

    if num_frames > len(frames):
        return frames
    random_frames = random.sample(frames, num_frames)
    return random_frames


class FaceRecognizer:
    """
    A class for recognizing faces from a live video feed and sending notifications when unknown faces are detected.

    This class uses OpenCV, face_recognition, and other modules to capture video frames, detect motion,
    recognize faces, and send email notifications when unknown faces are detected.

    Attributes:
        known_face_encodings (list): Encodings of known faces.
        face_encodings (list): Encodings of currently detected faces.
        unknown_face_frames (list): Frames containing unknown faces.
        last_known_detection_time (datetime): Timestamp of the last known face detection.
        last_unknown_detection_time (datetime): Timestamp of the last unknown face detection.
        detect_motion (MotionDetector): An instance of the MotionDetector class for motion detection.
        is_recording (bool): Indicates if video recording is in progress.
        save_video (VideoSaver): An instance of the VideoSaver class for saving video clips.
        email_sender (EmailSender): An instance of the EmailSender class for sending email notifications.
        count (int): Counter for recording duration.

    Methods:
        __init__():
            Initializes the FaceRecognizer class, loads known face encodings, and sets up email sender and motion detector.

        load_and_encode():
            Loads and encodes known faces from the specified directory.

        check_match(frame):
            Checks if the given frame matches any of the known faces.

        check_last_recognition_time(minutes=5):
            Checks the time elapsed since the last known face detection.

        handle_detected():
            Handles the detected unknown faces by sending email notifications and saving video clips.

        run_camera(camera_index=0):
            Starts camera, motion detection, and face recognition.
    """

    known_face_encodings = []
    face_encodings = []
    unknown_face_frames = []
    last_known_detection_time = None
    last_unknown_detection_time = None
    detect_motion = None
    is_recording = False
    save_video = None
    email_sender = None
    count = 0

    def __init__(self):

        """
        Initializes the FaceRecognizer class, loads known face encodings, and sets up email sender and motion detector.
        """

        self.detect_motion = MotionDetector()
        self.load_and_encode()
        self.email_sender = EmailSender(EMAIL, PASSWORD, RECEIVER)

    def load_and_encode(self):

        """
        Loads and encodes known faces from the specified directory.
        """

        print('Loading and encoding known faces...')
        filenames = next(walk(IMAGE_DIRECTORY), (None, None, []))[2]
        for filename in filenames:
            temp_face = face_recognition.load_image_file(f'{IMAGE_DIRECTORY}/{filename}')
            face_encoding_list = face_recognition.face_encodings(temp_face)
            if face_encoding_list:
                self.face_encodings.append(face_encoding_list[0])
            else:
                print(f'No face detected in {filename}')

        print('Done loading and encoding known faces...')

    def check_match(self, frame):

        """
        Checks if the given frame matches any of the known faces.

        Args:
            frame (numpy.ndarray): The frame to check for face matches.

        Returns:
            bool: True if a known face match is found, False otherwise.
        """

        if len(self.face_encodings) == 0:
            return None

        frame_encodings = face_recognition.face_encodings(frame)
        if not frame_encodings:
            return None

        for frame_encoding in frame_encodings:
            matches = face_recognition.compare_faces(self.face_encodings, frame_encoding, tolerance=TOLERANCE)
            if any(matches):
                return True
        return False

    def check_last_recognition_time(self, minutes=5):

        """
        Checks the time elapsed since the last known face detection.

        Args:
            minutes (int, optional): The time interval in minutes to check (default is 5).

        Returns:
            bool: True if the time interval has passed, False otherwise.
        """

        return self.last_known_detection_time is None or (
                datetime.datetime.now() - self.last_known_detection_time).seconds > minutes * 60

    def handle_detected(self):

        """
        Handles the detected unknown faces by sending email notifications and saving video clips.
        """

        images_to_send = get_random_frames(self.unknown_face_frames, RANDOM_FRAMES_TO_SEND)
        self.email_sender.send_email(images_to_send, self.last_unknown_detection_time.strftime('%Y-%m-%d_%H-%M-%S'))
        self.is_recording = False
        self.save_video = VideoSaver()
        self.save_video.save_video_clip(video_frames=self.unknown_face_frames)
        self.unknown_face_frames.clear()
        self.count = 0

    def run_camera(self, camera_index=0):

        """
        Starts camera, motion detection, and face recognition.

        Args:
            camera_index (int, optional): Index of the camera to use (default is 0).
        """

        print('Starting camera, motion detection, and face recognition...')
        video_capture = cv2.VideoCapture(camera_index)

        if not video_capture.isOpened():
            sys.exit('Video source not found...')

        while True:
            success, frame = video_capture.read()
            if not success:
                sys.exit('Error while reading frame...')

            cv2.imshow('Video', frame)

            motion_detected = self.detect_motion.detect_motion(frame)
            if motion_detected and self.check_last_recognition_time():
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                match = self.check_match(rgb_frame)

                if match:
                    self.last_known_detection_time = datetime.datetime.now()
                    self.unknown_face_frames.clear()
                    self.is_recording = False
                else:
                    self.last_unknown_detection_time = datetime.datetime.now()
                    self.is_recording = True
                    self.unknown_face_frames.append(frame)
            else:
                if self.is_recording:
                    self.count += 1

                if self.is_recording and self.count > RECORDING_DURATION_THRESHOLD and len(
                        self.unknown_face_frames) > 0:
                    self.handle_detected()

            if cv2.waitKey(1) & 0xFF == ord('q'):
                if self.is_recording and len(self.unknown_face_frames) > 0:
                    self.handle_detected()
                break
