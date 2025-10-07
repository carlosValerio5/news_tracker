class EmailAlreadyExistsException(Exception):
    """Exception raised when an email already exists in the database."""
    pass

class UserNotFoundException(Exception):
    """Exception raised when a user is not found in the database."""
    pass

class GoogleIDMismatchException(Exception):
    """Exception raised when there is a mismatch in Google ID."""
    pass