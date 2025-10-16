"""Helper functions for image processing and uploading to S3."""
import requests
from urllib.parse import urlparse
from requests import Response, RequestException

from exceptions.image_exceptions import ImageDownloadError

class ImageHelper:
    """Helper class for image processing and uploading to S3."""

    @staticmethod
    def download_image(image_url: str, max_retries: int = 3) -> Response:
        """
        Download an image from a given URL.

        :param image_url: URL of the image to download.
        :param max_retries: Number of retries for downloading the image.
        :return: Image content in bytes.
        :raises ImageDownloadError: If the image cannot be downloaded.
        """
        error = str()
        for _ in range(max_retries):
            try:
                response = requests.get(image_url, timeout=10)
                response.raise_for_status()
                return response
            except RequestException as e:
                error = str(e)
                continue

        raise ImageDownloadError(f"Error downloading image after {max_retries} attempts: {error}")

    @staticmethod
    def get_file_extension(url) -> str:
        """
        Extract file extension from URL.

        :param url: URL of the image.
        :return: File extension including the dot (e.g., '.jpg').
        """
        parsed = urlparse(url)
        path = parsed.path.lower()
        if path.endswith(('.jpg', '.jpeg')):
            return '.jpg'
        elif path.endswith('.png'):
            return '.png'
        elif path.endswith('.webp'):
            return '.webp'
        else:
            return '.jpg'  # default