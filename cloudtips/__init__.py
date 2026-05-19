"""
cloudtips — неофициальная асинхронная Python-библиотека для CloudTips.
"""

from .auth import CloudTipsAuth, CloudTipsAuthError
from .client import CloudTipsAPIError, CloudTipsClient
from .models import AccumulationSummary, Card, Donation, PayoutFeeInfo, ReceiverProfile, TokenData

__version__ = "0.4.1"
__all__ = [
    "CloudTipsAuth",
    "CloudTipsAuthError",
    "CloudTipsClient",
    "CloudTipsAPIError",
    "Donation",
    "Card",
    "PayoutFeeInfo",
    "AccumulationSummary",
    "ReceiverProfile",
    "TokenData",
]
