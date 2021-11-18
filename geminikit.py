import requests
import json
import base64
import hmac
import hashlib
import datetime
import time


class gemini_kit:

    def __init__(self, gemini_api_key: str, gemini_api_secret: str, account: str = None, sandbox: bool = False):
        self.gemini_api_key = gemini_api_key
        self.gemini_api_secret = gemini_api_secret.encode()
        self.account = account
        if sandbox:
            self.base_url = "https://api.sandbox.gemini.com"
        else:
            self.base_url = "https://api.gemini.com"

    def place_order(self, symbol: str, amount: str, price: str, side: str, order_type: str = "exchange limit", options: list = None, stop_price: str = None) -> dict:
        """
        symbol: 'btcusd', 'ethusd', etc...
        side: "buy", "sell"
        order_type: "exchange limit", "exchange stop limit"
        options (optional) list: "maker-or-cancel", "immediate-or-cancel", "fill-or-kill", "auction-only", "indication-of-interest"
        stop_price (optional)
        """

        self.endpoint = "/v1/order/new"
        self.url = self.base_url + self.endpoint

        self.payload_nonce = str(
            int(time.mktime(datetime.datetime.now().timetuple()) * 1000))
        self.payload = {
            "request": self.endpoint,
            "nonce": self.payload_nonce,
            "symbol": symbol,
            "amount": amount,
            "price": price,
            "side": side,
            "type": order_type
        }
        if options:
            self.payload["options"] = options
        if stop_price:
            self.payload["stop_price"] = stop_price
        if self.account:
            self.payload["account"] = self.account

        self.response = self.__send_payload()

        return self.response

    def cancel_order(self, order_id: str, all: bool or str = False) -> dict:
        """
        all (optional): True, False, 'session'

        Cancels orders, if all=True it will cancel all open orders,
        if all='session' it will cancel all orders from session
        """
        if all == True:
            self.endpoint = '/v1/order/cancel/all'
        elif type(all) == str:
            if all.lower() == 'session':
                self.endpoint = '/v1/order/cancel/session'
            else:
                raise ValueError(
                    f"Invalid argument {all} for all, must be: bool or 'session'")
        else:
            self.endpoint = "/v1/order/cancel"

        self.url = self.base_url + self.endpoint
        self.payload_nonce = str(
            int(time.mktime(datetime.datetime.now().timetuple()) * 1000))

        self.payload = {
            "nonce": self.payload_nonce,
            "order_id": order_id,
            "request": self.endpoint
        }

        if self.account:
            self.payload['account'] = self.account

        self.response = self.__send_payload()

        return self.response

    def order_status(self, order_id: str = None, include_trades: bool = True, client_order_id: str = None) -> dict:
        """
        Gets status of orders
        """
        self.endpoint = "/v1/order/status"

        self.url = self.base_url + self.endpoint
        self.payload_nonce = str(
            int(time.mktime(datetime.datetime.now().timetuple()) * 1000))
        if order_id:
            self.order_id = order_id
        elif client_order_id:
            self.order_id = client_order_id
        else:
            raise ValueError('Must supply either order_id or client_order_id')

        self.payload = {
            "nonce": self.payload_nonce,
            "order_id": self.order_id,
            "request": self.endpoint
        }

        if self.account:
            self.payload['account'] = self.account

        self.response = self.__send_payload()

        return self.response

    def get_active_orders(self) -> list:
        """
        Gets status of all active orders
        """
        self.endpoint = "/v1/orders"

        self.url = self.base_url + self.endpoint
        self.payload_nonce = str(
            int(time.mktime(datetime.datetime.now().timetuple()) * 1000))

        self.payload = {
            "nonce": self.payload_nonce,
            "request": self.endpoint
        }

        if self.account:
            self.payload['account'] = self.account

        self.response = self.__send_payload()

        return self.response

    def get_past_trades(self, symbol: str) -> list:
        """
        symbol: 'btcusd', 'ethusd', etc...

        Gets past trades for given symbol
        """
        self.endpoint = "/v1/mytrades"

        self.url = self.base_url + self.endpoint
        self.payload_nonce = str(
            int(time.mktime(datetime.datetime.now().timetuple()) * 1000))

        self.payload = {
            "nonce": self.payload_nonce,
            "request": self.endpoint,
            "symbol": symbol
        }

        if self.account:
            self.payload['account'] = self.account

        self.response = self.__send_payload()

        return self.response

    def get_balances(self) -> list:
        """
        Gets current balances
        """
        self.endpoint = "/v1/balances"

        self.url = self.base_url + self.endpoint
        self.payload_nonce = str(
            int(time.mktime(datetime.datetime.now().timetuple()) * 1000))

        self.payload = {
            "nonce": self.payload_nonce,
            "request": self.endpoint
        }

        if self.account:
            self.payload['account'] = self.account

        self.response = self.__send_payload()

        return self.response

    def get_notional_balances(self, currency: str = 'USD') -> list:
        """
        Gets current balances
        """
        self.currency = currency.lower()
        self.endpoint = f"/v1/notionalbalances/{self.currency}"

        self.url = self.base_url + self.endpoint
        self.payload_nonce = str(
            int(time.mktime(datetime.datetime.now().timetuple()) * 1000))

        self.payload = {
            "nonce": self.payload_nonce,
            "request": self.endpoint
        }

        if self.account:
            self.payload['account'] = self.account

        self.response = self.__send_payload()

        return self.response

    def get_accounts_in_master_group(self):
        """
        Get all accounts in master group
        """
        self.endpoint = "/v1/account/list"

        self.url = self.base_url + self.endpoint
        self.payload_nonce = str(
            int(time.mktime(datetime.datetime.now().timetuple()) * 1000))

        self.payload = {
            "nonce": self.payload_nonce,
            "request": self.endpoint
        }

        self.response = self.__send_payload()

        return self.response

    def __send_payload(self) -> dict:
        self.encoded_payload = json.dumps(self.payload).encode()
        self.b64 = base64.b64encode(self.encoded_payload)
        self.signature = hmac.new(
            self.gemini_api_secret, self.b64, hashlib.sha384).hexdigest()

        self.request_headers = {'Content-Type': "text/plain",
                                'Content-Length': "0",
                                'X-GEMINI-APIKEY': self.gemini_api_key,
                                'X-GEMINI-PAYLOAD': self.b64,
                                'X-GEMINI-SIGNATURE': self.signature,
                                'Cache-Control': "no-cache"}

        self.response = requests.post(self.url,
                                      data=None,
                                      headers=self.request_headers)
        self.response = self.response.json()

        return self.response
