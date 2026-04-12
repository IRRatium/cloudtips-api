from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Donation:
    transaction_id: int
    name: str
    amount: int          # рубли
    tg_id: int
    comment: str
    date: datetime

    @classmethod
    def from_dict(cls, data: dict) -> "Donation":
        raw_date = data["date"]
        try:
            dt = datetime.fromisoformat(raw_date)
        except ValueError:
            dt = datetime.fromisoformat(raw_date[:19])

        return cls(
            transaction_id=data["transaction_id"],
            name=data.get("name", ""),
            amount=data["amount"],
            tg_id=data.get("tg_id", 0),
            comment=data.get("comment", ""),
            date=dt,
        )

    def __str__(self) -> str:
        comment_part = f' — "{self.comment}"' if self.comment else ""
        return (
            f"[{self.date.strftime('%Y-%m-%d %H:%M')}] "
            f"{self.name} → {self.amount}₽{comment_part}"
        )


@dataclass
class Card:
    token: str              # токен для удаления и операций
    first_six: str          # первые 6 цифр (BIN)
    last_four: str          # последние 4 цифры
    card_type: str          # MIR / VISA / MASTERCARD
    expiration_date: str    # MM/YY
    issuer_code: str        # название банка
    is_default: bool        # карта по умолчанию для выплат
    commission_hint: str    # текст подсказки о комиссии

    @classmethod
    def from_dict(cls, data: dict) -> "Card":
        return cls(
            token=data["token"],
            first_six=data.get("firstSix", ""),
            last_four=data.get("lastFour", ""),
            card_type=data.get("cardType", ""),
            expiration_date=data.get("cardExpirationDate", ""),
            issuer_code=data.get("issuerCode", ""),
            is_default=data.get("isDefault", False),
            commission_hint=data.get("commissionHint", ""),
        )

    def __str__(self) -> str:
        default = " [по умолчанию]" if self.is_default else ""
        return (
            f"{self.card_type} *{self.last_four} "
            f"({self.issuer_code}, до {self.expiration_date}){default}"
        )


@dataclass
class PayoutFeeInfo:
    text: str                        # текст с описанием комиссий
    downgrade_condition: str
    tinkoff_commission_hint: str
    instant_payout_commission_text: str

    @classmethod
    def from_dict(cls, data: dict) -> "PayoutFeeInfo":
        return cls(
            text=data.get("text", ""),
            downgrade_condition=data.get("downGradeCondition", ""),
            tinkoff_commission_hint=data.get("tinkoffCommissionHint", ""),
            instant_payout_commission_text=data.get("instantPayoutCommissionText", ""),
        )


@dataclass
class AccumulationSummary:
    accumulated_amount: float    # накоплено (ещё не выведено)
    amount_to_deposit: float     # к зачислению
    commission: float            # сумма комиссии
    commission_percent: float    # процент комиссии
    next_payout_date: Optional[str]  # дата следующей выплаты (None если не запланирована)
    commission_hint: str         # текст подсказки

    @classmethod
    def from_dict(cls, data: dict) -> "AccumulationSummary":
        return cls(
            accumulated_amount=data.get("accumulatedAmount", 0.0),
            amount_to_deposit=data.get("amountToDeposit", 0.0),
            commission=data.get("commission", 0.0),
            commission_percent=data.get("commissionPercent", 0.0),
            next_payout_date=data.get("nextPayoutDate"),
            commission_hint=data.get("commissionHint", ""),
        )


@dataclass
class ReceiverProfile:
    user_id: str
    full_name: str
    phone_number: str
    photo_url: str
    payout_method: str          # "Instant" или "Accumulation"
    instant_payout_enabled: bool
    is_premium: bool
    onboarding_passed: bool
    gender: str
    work_place: Optional[str]
    work_position: Optional[str]
    birthday: Optional[str]
    created_date: str
    available_amount_min: float
    available_amount_max: float

    @classmethod
    def from_dict(cls, data: dict) -> "ReceiverProfile":
        available = data.get("availableAmount") or {}
        return cls(
            user_id=data.get("userId", ""),
            full_name=data.get("fullName", ""),
            phone_number=data.get("phoneNumber", ""),
            photo_url=data.get("photoUrl", ""),
            payout_method=data.get("payoutMethod", "Instant"),
            instant_payout_enabled=data.get("instantPayoutEnabled", False),
            is_premium=data.get("isPremium", False),
            onboarding_passed=data.get("onboardingPassed", False),
            gender=data.get("gender", "NotSpecified"),
            work_place=data.get("workPlace"),
            work_position=data.get("workPosition"),
            birthday=data.get("birthday"),
            created_date=data.get("createdDate", ""),
            available_amount_min=available.get("minimal", 0.0),
            available_amount_max=available.get("maximal", 0.0),
        )

    def __str__(self) -> str:
        return (
            f"{self.full_name} ({self.phone_number})\n"
            f"Метод выплат: {self.payout_method} | "
            f"Премиум: {'да' if self.is_premium else 'нет'} | "
            f"Лимиты: {self.available_amount_min}₽ — {self.available_amount_max}₽"
        )


    """Новые токены, которые библиотека передаёт в on_token_refresh."""
    access_token: str
    refresh_token: str
    expires_at: float   # unix timestamp
