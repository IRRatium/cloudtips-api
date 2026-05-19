"""
Аутентификация CloudTips — управление access/refresh токенами.
"""
import asyncio
import time
from typing import Callable, Optional

import aiohttp

from .models import TokenData

_TOKEN_URL = "https://identity.cloudtips.ru/connect/token"
_CLIENT_ID = "MobilePhone"
_EXPIRE_BUFFER = 120  # обновляем токен за 2 минуты до истечения


class CloudTipsAuth:
    """
    Управляет access/refresh токенами CloudTips.

    Параметр ``on_token_refresh`` — колбэк, вызываемый после каждого
    успешного обновления токенов. Refresh-токен одноразовый, поэтому
    обязательно сохраняйте новые значения.

    Пример::

        async def save_tokens(token_data: TokenData):
            config["cloudtips_token"] = token_data.access_token
            config["cloudtips_refresh_token"] = token_data.refresh_token
            config["cloudtips_expires_at"] = token_data.expires_at
            await write_config(config)

        auth = CloudTipsAuth(
            token="eyJ...",
            refresh_token="abc123...",
            expires_at=1776099728.0,
            on_token_refresh=save_tokens,
        )
    """

    def __init__(
        self,
        token: str,
        refresh_token: str,
        expires_at: float,
        on_token_refresh: Optional[Callable[[TokenData], None]] = None,
    ) -> None:
        self._token = token
        self._refresh_token = refresh_token
        self._expires_at = expires_at
        self._on_token_refresh = on_token_refresh
        self._lock = asyncio.Lock()  # Защита от Race Condition при параллельных запросах

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    async def get_token(self) -> str:
        """Возвращает актуальный access-токен, автоматически обновляя при необходимости."""
        if self._is_expired():
            async with self._lock:
                # Повторная проверка: пока текущий таск ждал лока, другой таск уже мог обновить токен
                if self._is_expired():
                    await self.refresh()
        return self._token

    @property
    def expires_at(self) -> float:
        return self._expires_at

    async def refresh(self) -> TokenData:
        """Принудительно обновляет токены через CloudTips Identity Server."""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                _TOKEN_URL,
                data={
                    "grant_type":    "refresh_token",
                    "refresh_token": self._refresh_token,
                    "client_id":     _CLIENT_ID,
                },
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                await _raise_for_status(response)
                data = await response.json()

        token_data = TokenData(
            access_token=data["access_token"],
            refresh_token=data["refresh_token"],
            expires_at=time.time() + data["expires_in"],
        )

        self._token = token_data.access_token
        self._refresh_token = token_data.refresh_token
        self._expires_at = token_data.expires_at

        if self._on_token_refresh:
            result = self._on_token_refresh(token_data)
            # поддержка как async, так и обычных колбэков
            if hasattr(result, "__await__"):
                await result

        return token_data

    async def headers(self) -> dict:
        """Готовые Authorization-заголовки для запросов."""
        return {
            "Authorization": f"Bearer {await self.get_token()}",
            "Content-Type":  "application/json",
        }

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _is_expired(self) -> bool:
        return time.time() >= self._expires_at - _EXPIRE_BUFFER


async def _raise_for_status(response: aiohttp.ClientResponse) -> None:
    if not response.ok:
        try:
            detail = await response.json()
        except Exception:
            detail = await response.text()
        raise CloudTipsAuthError(
            f"Ошибка при обновлении токена: {response.status} — {detail}"
        )


class CloudTipsAuthError(Exception):
    """Ошибка аутентификации CloudTips."""
    pass
