import os
from datetime import datetime, timedelta
import requests
import longbridge as lb
from longbridge.openapi import Config
from longbridge.openapi import TradeContext, Config, OAuthBuilder



PROXY = 'http://127.0.0.1:7897'

if __name__ == "__main__":
    os.environ['HTTP_PROXY'] = PROXY
    os.environ['HTTPS_PROXY'] = PROXY
    #response = requests.post(
    #    "https://openapi.longbridge.com/oauth2/register",
    #    json={
    #        "redirect_uris": ["http://localhost:60355/callback"],
    #        "token_endpoint_auth_method": "none",
    #        "grant_types": ["authorization_code", "refresh_token"],
    #        "response_types": ["code"],
    #        "client_name": "My Longbridge OpenAPI",
    #    },
    #)
    #print(response.status_code)
    #print(response.json())
    #client_id = response.json().get("client_id")

    #oauth = lb.openapi.OAuthBuilder(client_id).build(
    #    lambda url: print(f"Open this URL to authorize: {url}"))
    #config = lb.openapi.OpenAPIConfig.from_oauth(oauth)
    #print(f"Config: {config}")

    config = Config.from_apikey(
        os.getenv("LONGBRIDGE_APP_KEY"),
        os.getenv("LONGBRIDGE_APP_SECRET"),
        os.getenv("LONGBRIDGE_ACCESS_TOKEN"))
    print(f'Config: {config}')
    ctx = TradeContext(config)
    resp = ctx.account_balance()
    print(resp)
    # Expire 3 years from now
    #new_token = config.refresh_access_token(expired_at=datetime.now() + timedelta(days=365 * 3))
    #print("New access token:", new_token)
    # Use the new token to build a new Config, or persist it as LONGBRIDGE_ACCESS_TOKEN
    #new_config = Config.from_apikey("YOUR_APP_KEY", "YOUR_APP_SECRET", new_token)