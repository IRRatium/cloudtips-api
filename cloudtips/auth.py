import time
from typing import Callable, Optional

import requests

from .models import TokenData

_TOKEN_URL = "https://identity.cloudtips.ru/connect/token"
_CLIENT_ID = "MobilePhone"
_EXPIRE_BUFFER = 120  # обновляем токен за 2 минуты до истечения


class CloudTipsAuth:
    """
    Управляет access/refresh токенами CloudTips.

    Параметр `on_token_refresh` — это колбэк, который вызывается каждый раз
    после успешного обновления токенов. Используйте его, чтобы сохранить
    новые токены в файл/БД/переменные окружения — refresh-токен одноразовый!

    Пример::

        def save_tokens(token_data: TokenData):
            config["cloudtips_token"] = token_data.access_token
            config["cloudtips_refresh_token"] = token_data.refresh_token
            config["cloudtips_expires_at"] = token_data.expires_at
            save_config(config)

        auth = CloudTipsAuth(
            token="...",
            refresh_token="...",
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

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    @property
    def token(self) -> str:
        """Возвращает актуальный access-токен, автоматически обновляя при необходимости."""
        if self._is_expired():
            self.refresh()
        return self._token

    @property
    def expires_at(self) -> float:
        return self._expires_at

    def refresh(self) -> TokenData:
        """Принудительно обновляет токены через CloudTips Identity Server."""
        response = requests.post(
            _TOKEN_URL,
            data={
                "grant_type": "refresh_token",
                "refresh_token": self._refresh_token,
                "client_id": _CLIENT_ID,
            },
            timeout=10,
        )
        _raise_for_status(response)

        data = response.json()
        token_data = TokenData(
            access_token=data["access_token"],
            refresh_token=data["refresh_token"],
            expires_at=time.time() + data["expires_in"],
        )

        self._token = token_data.access_token
        self._refresh_token = token_data.refresh_token
        self._expires_at = token_data.expires_at

        if self._on_token_refresh:
            self._on_token_refresh(token_data)

        return token_data

    def headers(self) -> dict:
        """Готовые Authorization-заголовки для запросов."""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _is_expired(self) -> bool:
        return time.time() >= self._expires_at - _EXPIRE_BUFFER


def _raise_for_status(response: requests.Response) -> None:
    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        try:
            detail = response.json()
        except Exception:
            detail = response.text
        raise CloudTipsAuthError(
            f"Ошибка при обновлении токена: {response.status_code} — {detail}"
        ) from e


class CloudTipsAuthError(Exception):
    """Ошибка аутентификации CloudTips."""
