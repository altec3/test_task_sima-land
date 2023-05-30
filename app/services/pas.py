import base64
import hashlib
import hmac
from typing import Dict


class PasService:

    def __init__(self, config: Dict[str, dict]):
        self._config: Dict[str, dict] = config

    async def _get_options(self) -> Dict[str, str]:
        return self._config['hashlib']

    async def _string_to_bytes(self, str_value: str) -> bytes:
        return str_value.encode('utf-8')

    async def _bytes_to_string(self, bytes_value: bytes) -> str:
        return bytes_value.decode('utf-8')

    async def encode_password(self, password: str) -> str:
        options = await self._get_options()
        password = await self._string_to_bytes(password)
        salt = await self._string_to_bytes(options['salt'])

        hash_digest = hashlib.pbkdf2_hmac(
            hash_name=options['hash_name'],
            password=password,
            salt=salt,
            iterations=int(options['iterations'])
        )

        return await self._bytes_to_string(base64.b64encode(hash_digest))

    async def compare_passwords(self, password_hash: str, other_password: str) -> bool:
        options = await self._get_options()
        password_hash = await self._string_to_bytes(password_hash)
        other_password = await self._string_to_bytes(other_password)
        salt = await self._string_to_bytes(options['salt'])

        return hmac.compare_digest(
            base64.b64decode(password_hash),
            hashlib.pbkdf2_hmac(
                hash_name=options['hash_name'],
                password=other_password,
                salt=salt,
                iterations=int(options['iterations']),
            )
        )
