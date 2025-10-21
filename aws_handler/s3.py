"""AWS S3 Handler Module"""

import boto3
from datetime import datetime
from botocore.exceptions import BotoCoreError, ClientError

from exceptions.s3 import S3BucketServiceError
from exceptions.image import ImageDownloadError
from helpers.image_helper import ImageHelper


class S3Handler:
    """Handler for AWS S3 operations."""

    def __init__(
        self, bucket_name: str, cdn_url: str, region_name: str = "us-east-2"
    ) -> None:
        """
        Initialize the S3 client and specify the bucket name.

        :param bucket_name: Name of the S3 bucket.
        :param cdn_url: CDN URL for accessing the bucket content.
        :param region_name: AWS region where the bucket is located.
        """
        try:
            self.s3 = boto3.client("s3", region_name=region_name)
        except Exception as e:
            raise S3BucketServiceError(f"Error initializing S3 client: {e}")
        self.bucket_name = bucket_name
        self.cdn_url = cdn_url
        self.region_name = region_name

    def upload_thumbnail(self, image_url: str, article_id: int) -> str:
        """
        Upload a thumbnail image to the S3 bucket.

        :param image_url: URL of the image to upload.
        :param article_id: ID of the article associated with the image.
        """
        try:
            response = ImageHelper.download_image(image_url)

            file_extension = ImageHelper.get_file_extension(image_url)
            s3_key = f"thumbnails/{datetime.now().strftime('%Y/%m/%d')}/{article_id}{file_extension}"
            metadata = {
                "article_id": str(article_id),
                "original_url": image_url,
                "uploaded_at": datetime.now().isoformat(),
            }

            self.s3.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=response.content,
                ContentType=response.headers.get("Content-Type", "image/jpeg"),
                CacheControl="max-age=31536000",
                Metadata=metadata,
            )

            # Location in bucket
            return f"https://{self.cdn_url}/{s3_key}"

        except BotoCoreError as e:
            raise S3BucketServiceError(f"Error uploading to S3: {e}")
        except ClientError as e:
            raise S3BucketServiceError(f"Client error during S3 upload: {e}")
        except (Exception, ImageDownloadError):
            raise
