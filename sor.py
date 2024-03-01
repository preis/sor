import os
import logging
import requests
from dotenv import load_dotenv

from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

logger = logging.getLogger('Simple OAuth Request')


class SimpleOAuthRequest:
    """Permite estabelecer ligação a microserviços protegidos por OAuth.

    :author: Paulo Faria Reis (2024-02-29)
    :version: 20240229 Paulo Faria Reis
    """
    client = None
    oauth = None
    token = None
    client_id = None
    client_secret = None
    realm_base_url = None
    openid_configuration = None
    auto_refresh = True

    def __init__(self, auto_refresh=False):
        self._collect_env()
        self._fetch_client_config()
        self._init_client()
        self._fetch_token()
        self.auto_refresh = auto_refresh

    def _guardar_token(self, token):
        """Guarda o token. TODO: persistir em sessão ou BD."""
        self.token = token

    def _collect_env(self):
        load_dotenv()
        self.client_id = os.getenv("OIDC_CLIENT_ID")
        self.client_secret = os.getenv("OIDC_CLIENT_SECRET")
        self.realm_base_url = os.getenv("OIDC_REALM_BASE_URL")

    def _fetch_client_config(self):
        resp = requests.get(f"{self.realm_base_url}/.well-known/openid-configuration")
        self.openid_configuration = resp.json()

    def _init_client(self):
        self.client = BackendApplicationClient(client_id=self.client_id)
        if self.auto_refresh:
            extra_kwargs = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            }
            self.oauth = OAuth2Session(
                self.client_id,
                token=self.token,
                auto_refresh_url=f"{self.realm_base_url}/protocol/openid-connect/token",
                auto_refresh_kwargs=extra_kwargs,
                token_updater=self._guardar_token
            )
        else:
            self.oauth = OAuth2Session(client=self.client)

    def _fetch_token(self):
        token = self.oauth.fetch_token(
            token_url=f"{self.realm_base_url}/protocol/openid-connect/token",
            client_id=self.client_id,
            client_secret=self.client_secret
        )
        self._guardar_token(token)

    def _fetch_user_info(self):
        try:
            resp = self.oauth.get(self.openid_configuration["userinfo_endpoint"])
            return resp.json()
        except Exception as ex:
            logger.exception(ex)
            return None

    def get_json(self, url):
        try:
            resp = self.oauth.get(url)
            return resp.json()
        except Exception as ex:
            logger.exception(ex)
            return None
