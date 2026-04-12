from dataclasses import dataclass, field
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
        # Убираем offset вида +03:00 → datetime aware через fromisoformat (3.11+)
        # или ручной парсинг для 3.9/3.10
        try:
            dt = datetime.fromisoformat(raw_date)
        except ValueError:
            # fallback: обрезаем offset
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
class TokenData:
    """Новые токены, которые библиотека передаёт в on_token_refresh."""
    access_token: str
    refresh_token: str
    expires_at: float   # unix timestamp
