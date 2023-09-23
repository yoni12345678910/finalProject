import smtplib
from email.message import EmailMessage
from PIL import Image
import io


class EmailSender:
    """
    A class for sending emails with image attachments using Gmail's SMTP server.

    This class is designed to simplify the process of sending emails with image attachments.
    It requires a Gmail email address, its corresponding password, and the recipient's email
    address. The class provides a method to send an email with an attached image.

    Attributes:
        email (str): The Gmail email address used for sending the email.
        password (str): The password associated with the Gmail email address.
        receiver (str): The recipient's email address.

    Methods:
        send_email(image_array, detection_time):
            Sends an email with an attached image to the specified recipient.
            Args:
                image_array (str): The path to the images to be attached to the email.
                detection_time (str): The time of the detection.
    """

    def __init__(self, email, password, receiver):
        """
        Initializes the EmailSender class with the provided email, password, and receiver.
        Args:
            email (str): The Gmail email address used for sending the email.
            password (str): The password associated with the Gmail email address.
            receiver (str): The recipient's email address.
        """

        self.email = email
        self.password = password
        self.receiver = receiver

    def send_email(self, image_array, detection_time):
        """
        Sends an email with an attached image to the specified recipient.
        Args:
            image_array (list): The images to be attached to the email.
            detection_time (str): The time of the detection.
        """

        email_message = EmailMessage()
        email_message['Subject'] = 'New detection'
        email_message.set_content(f'Hey, have a look at a new detection at {detection_time}')

        for image in image_array:
            image = Image.fromarray(image)
            image_bytes = io.BytesIO()
            image.save(image_bytes, format='JPEG')
            image_bytes = image_bytes.getvalue()
            email_message.add_attachment(image_bytes, maintype='image', subtype='jpeg')

        gmail = smtplib.SMTP('smtp.gmail.com', 587)
        gmail.ehlo()
        gmail.starttls()
        gmail.login(self.email, self.password)
        gmail.sendmail(self.email, self.receiver, email_message.as_string())

        print('Email sent successfully')
        gmail.quit()
