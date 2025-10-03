from enum import Enum

class Scope(str, Enum):
    '''Defines the scopes for JWTs.'''
    READ_NEWS = "read:news"