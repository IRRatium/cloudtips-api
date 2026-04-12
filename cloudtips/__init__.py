"""
cloudtips — неофициальная Python-библиотека для CloudTips.
"""

from .auth import CloudTipsAuth, CloudTipsAuthError
from .client import CloudTipsAPIError, CloudTipsClient
from .models import AccumulationSummary, Card, Donation, PayoutFeeInfo, TokenData

__version__ = "0.2.0"
__all__ = [
    "CloudTipsAuth",
    "CloudTipsAuthError",
    "CloudTipsClient",
    "CloudTipsAPIError",
    "Donation",
    "Card",
    "PayoutFeeInfo",
    "AccumulationSummary",
    "TokenData",
]
