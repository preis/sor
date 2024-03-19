# Simple OAuth (Openid) Requests

Utiliza o requests-oauthlib para simplificar ligações a endpoints que tenham autenticação por OAuth2.
Se suportado pelo serviço implementa o refrescamento automático do token.


## Como utilizar

Pode ser utilizado de forma independente, por exemplo num Jupyter Notebook, ou script Python.
Ver exemplos na pasta ``nbs``.

Precisa de ter as variáveis de ambiente configuradas.


## Variáveis de ambiente

| Nome                | Descrição                                       |
|---------------------|-------------------------------------------------|
| OIDC_REALM_BASE_URL | URL base do servidor OAuth                      |
| OIDC_CONFIG         | URl para obter a configuração do servidor OAuth |
| OIDC_CLIENT_ID      | Client ID a utilizar na autnteicação            |
| OIDC_CLIENT_SECRET  | Secret associado ao Cliente ID                  |
