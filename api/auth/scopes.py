from enum import Enum


class Scope(str, Enum):
    """Defines the scopes for JWTs."""

    USER = "u"
    ADMIN = "a"
