from __future__ import annotations

from wallet import Wallet


class User:

    def __init__(
        self,
        first_name: str,
        last_name: str,
        username: str,
        email: str,
        password_hash: str,
    ):
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.email = email
        self.password_hash = password_hash
 
        self.wallets: list[Wallet] = []
        self.remember_token = None
        self.settings = {}
