import hashlib
import hmac
import json
import logging
from typing import Any

import aiohttp

logger = logging.getLogger(__name__)

CRYPTO_PAY_API_URL = "https://pay.crypt.bot/api"
CRYPTO_PAY_TESTNET_API_URL = "https://testnet-pay.crypt.bot/api"


class CryptoPayService:
    def __init__(self, token: str, testnet: bool = False) -> None:
        self._token = token
        self._api_url = CRYPTO_PAY_TESTNET_API_URL if testnet else CRYPTO_PAY_API_URL
        self._session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                headers={"Crypto-Pay-API-Token": self._token}
            )
        return self._session

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()

    async def _request(self, method: str, params: dict | None = None) -> dict[str, Any]:
        session = await self._get_session()
        url = f"{self._api_url}/{method}"
        async with session.get(url, params=params) as resp:
            data = await resp.json()
            if not data.get("ok"):
                logger.error("Crypto Pay API error: %s", data)
                raise RuntimeError(f"Crypto Pay API error: {data}")
            return data["result"]

    async def create_invoice(
        self,
        amount: float,
        currency: str = "USDT",
        description: str = "Channel subscription (1 month)",
        payload: str = "",
    ) -> dict[str, Any]:
        session = await self._get_session()
        url = f"{self._api_url}/createInvoice"
        params = {
            "currency_type": "crypto",
            "asset": currency,
            "amount": str(amount),
            "description": description,
            "payload": payload,
            "expires_in": 3600,
        }
        async with session.get(url, params=params) as resp:
            data = await resp.json()
            if not data.get("ok"):
                logger.error("Failed to create invoice: %s", data)
                raise RuntimeError(f"Failed to create invoice: {data}")
            return data["result"]

    async def get_invoices(self, invoice_ids: str | None = None) -> dict[str, Any]:
        params = {}
        if invoice_ids:
            params["invoice_ids"] = invoice_ids
        return await self._request("getInvoices", params)

    def verify_webhook_signature(self, body: bytes, signature: str) -> bool:
        secret = hashlib.sha256(self._token.encode()).digest()
        check_string = body.decode("utf-8")
        computed = hmac.new(
            secret, check_string.encode("utf-8"), hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(computed, signature)

    @staticmethod
    def parse_webhook_payload(body: bytes) -> dict[str, Any]:
        data = json.loads(body)
        return data
