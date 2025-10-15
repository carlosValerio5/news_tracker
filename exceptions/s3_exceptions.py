class S3BucketServiceError(Exception):
    """Custom exception for S3 bucket service errors."""
    pass

class S3UploadError(Exception):
    """Custom exception for S3 upload errors."""
    pass

class ImageDownloadError(Exception):
    """Custom exception for image download errors."""
    pass