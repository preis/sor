import os
import logging
import requests
from dotenv import load_dotenv

from oauthlib.oauth2 import BackendApplicationClient
from requests import ConnectTimeout
from requests_oauthlib import OAuth2Session

logger = logging.getLogger('Simple OAuh Requests')


class SimpleOAuth2Requests:
    """Permite estabelecer ligação a microserviços protegidos por OAuth.

    Utiliza requests-oauthlib: https://github.com/requests/requests-oauthlib

    :author: Paulo Faria Reis (2024-02-29)
    :version: 20240301 Paulo Faria Reis
    """
    token = {}
    client_id = None
    oauth_client = None
    oauth_session = None
    client_secret = None
    oid_config_url = None
    realm_base_url = None
    token_endpoint = None
    userinfo_endpoint = None
    openid_configuration = {}

    def __init__(self, auto_refresh=False):
        self.auto_refresh = auto_refresh
        self._collect_env()
        self._fetch_client_config()
        self._init_client()
        self._fetch_token()

    def _guardar_token(self, new_token):
        """Guarda o token.

        TODO: persistir em sessão ou BD.

        :author: Paulo Faria Reis (2024-02-29)
        :version: 20240229 Paulo Faria Reis
        """
        # os.environ["OAUTH_TOKEN"] = new_token
        self.token = new_token

    def _collect_env(self):
        """Carrega as variáveis de ambiente.

        :author: Paulo Faria Reis (2024-02-29)
        :version: 20240229 Paulo Faria Reis
        """
        load_dotenv()
        self.client_id = os.getenv("OID_CLIENT_ID")
        self.client_secret = os.getenv("OID_CLIENT_SECRET")
        self.realm_base_url = os.getenv("OID_REALM_BASE_URL")
        self.oid_config_url = os.getenv("OID_CONFIG_URL")

    def _fetch_client_config(self):
        """Obtem a configuração do servidor de Openid.

        Utiliza o requests "normal".

        :author: Paulo Faria Reis (2024-02-29)
        :version: 20240229 Paulo Faria Reis
        """
        resp = requests.get(f"{self.realm_base_url}/.well-known/openid-configuration")
        if resp.status_code == 200:
            self.openid_configuration = resp.json()
        # Definir o URL para obter o Token
        self.token_endpoint = self.openid_configuration.get(
            "token_endpoint",
            f"{self.realm_base_url}/protocol/openid-connect/token"
        )
        # Definir o URL para obter a User Info
        self.userinfo_endpoint = self.openid_configuration.get(
            "userinfo_endpoint",
            f"{self.realm_base_url}/protocol/openid-connect/userinfo"
        )

        self.openid_configuration = resp.json()

    def _init_client(self):
        """Inicializa o cliente e sessão OAuth.

        :author: Paulo Faria Reis (2024-02-29)
        :version: 20240229 Paulo Faria Reis
        """
        self.oauth_client = BackendApplicationClient(client_id=self.client_id)
        if self.auto_refresh:
            self.oauth_session = OAuth2Session(
                client=self.oauth_client,
                token=self.token,
                auto_refresh_url=self.token_endpoint,
                auto_refresh_kwargs={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
                token_updater=self._guardar_token,
            )
        else:
            self.oauth_session = OAuth2Session(client=self.oauth_client)

    def _fetch_token(self):
        """Faz um pedido de token.

        :author: Paulo Faria Reis (2024-02-29)
        :version: 20240229 Paulo Faria Reis
        """
        token = self.oauth_session.fetch_token(
            token_url=self.token_endpoint,
            client_id=self.client_id,
            client_secret=self.client_secret,
        )
        self._guardar_token(token)

    def _fetch_user_info(self):
        """Obtem a Informação do utilizador autenticado.

        :author: Paulo Faria Reis (2024-02-29)
        :version: 20240229 Paulo Faria Reis
        """
        try:
            resp = self.oauth_session.get(self.userinfo_endpoint)
            return resp.json()
        except Exception as ex:
            logger.exception(ex)
            return None

    def get_json(self, url):
        """Faz uma ligação GET a um endpoint que devolve JSON.

        :author: Paulo Faria Reis (2024-02-29)
        :version: 20240301 Paulo Faria Reis
        """
        try:
            resp = self.oauth_session.get(url)
            return resp.json()
        except ConnectTimeout as ex:
            logger.exception(ex)
            return {
                "error": "Timeout",
            }
        except Exception as ex:
            logger.exception(ex)
            return None

    def post_json(self, url, **kwargs):
        """Faz uma ligação POST a um endpoint que devolve JSON.

        :author: Paulo Faria Reis (2024-03-01)
        :version: 20240301 Paulo Faria Reis
        """
        try:
            resp = self.oauth_session.post(url, **kwargs)
            return resp.json()
        except ConnectTimeout as ex:
            logger.exception(ex)
            return {
                "error": "Timeout",
            }
        except Exception as ex:
            logger.exception(ex)
            return None
