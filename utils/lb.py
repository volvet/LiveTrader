import os
import time
from datetime import datetime, timedelta
from decimal import Decimal
import requests
import longbridge as lb
from longbridge.openapi import Config
from longbridge.openapi import TradeContext, Config, OAuthBuilder
from longbridge.openapi import QuoteContext, SubType, PushQuote
from longbridge.openapi import Period, AdjustType, TradeSessions
from longbridge.openapi import OrderType, OrderSide, TimeInForceType
from net import *


def on_quote(symbol: str, event: PushQuote):
    print(f"Quote received: {event}")


if __name__ == "__main__":
    setup_proxy(PROXY)
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

    # Expire 3 years from now
    #new_token = config.refresh_access_token(expired_at=datetime.now() + timedelta(days=365 * 3))
    #print("New access token:", new_token)
    # Use the new token to build a new Config, or persist it as LONGBRIDGE_ACCESS_TOKEN
    #new_config = Config.from_apikey("YOUR_APP_KEY", "YOUR_APP_SECRET", new_token)

    config = Config.from_apikey(
        os.getenv("LONGBRIDGE_APP_KEY"),
        os.getenv("LONGBRIDGE_APP_SECRET"),
        os.getenv("LONGBRIDGE_ACCESS_TOKEN"))
    
    #ctx = QuoteContext(config)
    #candlesticks = ctx.history_candlesticks_by_offset(
    #    "700.HK",
    #    Period.Day,
    #    AdjustType.NoAdjust,
    #    False,
    #    10,
    #    datetime(2023, 8, 18),
    #    TradeSessions.Intraday,
    #)
    #for candlestick in candlesticks:
    #    print(candlestick)

    #ctx.set_on_quote(on_quote)
    #resp = ctx.static_info(['QQQ.US', 'AAPL.US'])
    #print(f"{resp}")
    #ctx.subscribe(["AAPL.US"], [SubType.Quote]) # AAPL.US is Apple US
    #time.sleep(30)
    ctx = TradeContext(config)
    resp = ctx.account_balance()
    print(resp)

    #resp = ctx.submit_order(
    #    symbol = "BRK.B.US",
    #    order_type =OrderType.LO,
    #    side = OrderSide.Buy,
    #    submitted_quantity = Decimal(10),
    #    submitted_price = Decimal(460),
    #    time_in_force = TimeInForceType.Day,
    #    remark="Hello from Python SDK",
    #)
    #print(resp)