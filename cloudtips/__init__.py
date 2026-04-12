"""
cloudtips — неофициальная Python-библиотека для CloudTips.
"""

from .auth import CloudTipsAuth, CloudTipsAuthError
from .client import CloudTipsAPIError, CloudTipsClient
from .models import Donation, TokenData

__version__ = "0.1.0"
__all__ = [
    "CloudTipsAuth",
    "CloudTipsAuthError",
    "CloudTipsClient",
    "CloudTipsAPIError",
    "Donation",
    "TokenData",
]
