"""
src/brokers/angelone/auth.py
Automated daily authentication for Angel One SmartAPI using TOTP.
Handles session generation, JWT token retrieval, and token refresh.

Angel One SmartAPI login flow:
  1. Generate TOTP from user's TOTP secret
  2. Call generateSession(clientcode, password, totp) -> jwtToken + refreshToken
  3. Use jwtToken for all subsequent API calls
  4. Refresh token before expiry using generateToken(refreshToken)
"""
import pyotp
import logging
from typing import Optional, Tuple

logger = logging.getLogger("TradeBot.AngelOneAuth")


class AngelOneAuthenticator:
    def __init__(
        self,
        api_key: str,
        client_id: str,
        password: str,
        totp_secret: str,
    ):
        self.api_key = api_key
        self.client_id = client_id
        self.password = password
        self.totp_secret = totp_secret

    def generate_totp(self) -> str:
        """Generates current 6-digit TOTP code from the Angel One authenticator secret."""
        totp = pyotp.TOTP(self.totp_secret)
        code = totp.now()
        logger.info(f"Generated TOTP for Angel One client {self.client_id}: {code[:2]}****")
        return code

    def create_session(self, smart_api_instance) -> Tuple[Optional[str], Optional[str]]:
        """
        Authenticates with Angel One SmartAPI and returns (jwt_token, refresh_token).
        Uses the SmartConnect object passed in.
        """
        try:
            totp_code = self.generate_totp()

            data = smart_api_instance.generateSession(
                clientCode=self.client_id,
                password=self.password,
                totp=totp_code,
            )

            if data and data.get("status"):
                jwt_token = data["data"]["jwtToken"]
                refresh_token = data["data"]["refreshToken"]
                feed_token = smart_api_instance.getfeedToken()
                logger.info(
                    f"Angel One session created successfully. "
                    f"Feed token obtained: {'Yes' if feed_token else 'No'}"
                )
                return jwt_token, refresh_token
            else:
                error_msg = data.get("message", "Unknown error") if data else "No response"
                logger.error(f"Angel One session generation failed: {error_msg}")
                return None, None

        except Exception as e:
            logger.error(f"Angel One authentication exception: {e}", exc_info=True)
            return None, None

    def refresh_session(self, smart_api_instance, refresh_token: str) -> Optional[str]:
        """Refreshes the JWT token before expiry."""
        try:
            token_data = smart_api_instance.generateToken(refresh_token)
            if token_data and token_data.get("status"):
                new_jwt = token_data["data"]["jwtToken"]
                logger.info("Angel One JWT token refreshed successfully.")
                return new_jwt
            else:
                logger.warning("Angel One token refresh failed; re-authentication may be required.")
                return None
        except Exception as e:
            logger.error(f"Angel One token refresh exception: {e}")
            return None
