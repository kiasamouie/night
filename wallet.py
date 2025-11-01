import json, os
from pycardano import (
    HDWallet,
    Network,
    Address,
    PaymentVerificationKey,
    PaymentSigningKey,
    StakeVerificationKey,
)

WALLET_FILE = "wallet.json"

class WalletManager:
    def __init__(self, network: Network = Network.TESTNET):
        self.network = network
        self.wallet = None

    def create_or_load_wallet(self, path: str = WALLET_FILE):
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                mnemonic = data["mnemonic"]
                print("Loaded existing wallet from", path)
                self.wallet = HDWallet.from_mnemonic(mnemonic)
        else:
            print("Creating new wallet...")
            mnemonic = HDWallet.generate_mnemonic(language="english", strength=256)
            self.wallet = HDWallet.from_mnemonic(mnemonic)
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"mnemonic": mnemonic}, f, indent=2)
            print("\n--- BACKUP THESE 24 WORDS ---")
            print(mnemonic)
            print("---------------------------------\n")

    def get_payment_key(self):
        node = self.wallet.derive_from_path("m/1852'/1815'/0'/0/0")
        seed = node.xprivate_key[-32:]
        return PaymentSigningKey.from_primitive(seed)

    def _stake_node(self):
        return self.wallet.derive_from_path("m/1852'/1815'/0'/2/0")

    def get_address(self) -> str:
        pay_node = self.wallet.derive_from_path("m/1852'/1815'/0'/0/0")
        pay_pub_bytes = pay_node.public_key
        stk_pub_bytes = self._stake_node().public_key

        pay_vkey = PaymentVerificationKey.from_primitive(pay_pub_bytes)
        stk_vkey = StakeVerificationKey.from_primitive(stk_pub_bytes)
        addr = Address(pay_vkey.hash(), stk_vkey.hash(), network=self.network)
        return str(addr)

    def get_pubkey_hex(self) -> str:
        pay_node = self.wallet.derive_from_path("m/1852'/1815'/0'/0/0")
        pay_pub_bytes = pay_node.public_key
        pay_vkey = PaymentVerificationKey.from_primitive(pay_pub_bytes)
        return pay_vkey.to_primitive().hex()
