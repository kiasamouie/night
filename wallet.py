import json
import os

WALLET_FILE = "wallets.json"


class WalletManager:
    def __init__(self, path: str = WALLET_FILE):
        self.path = path
        self.wallets = self._load_wallets()

    def _load_wallets(self):
        if not os.path.exists(self.path):
            raise FileNotFoundError(f"Wallet file not found: {self.path}")

        with open(self.path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if "wallets" not in data or not isinstance(data["wallets"], list):
            raise ValueError("Invalid wallet JSON structure. Expected key 'wallets'.")

        return data["wallets"]

    def list_wallets(self):
        """Return a list of all wallet entries."""
        return self.wallets

    def get_wallet(self, index: int = 0):
        """Get a specific wallet by index (default first)."""
        if index < 0 or index >= len(self.wallets):
            raise IndexError("Wallet index out of range.")
        return self.wallets[index]

    def get_address(self, index: int = 0):
        return self.get_wallet(index)["address"]

    def get_pubkey_hex(self, index: int = 0):
        return self.get_wallet(index).get("pubkey_hex")
