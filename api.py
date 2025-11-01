import requests
import hashlib
import binascii

API_BASE = "https://scavenger.prod.gd.midnighttge.io"

class MidnightMiner:
    def __init__(self, address: str, pubkey_hex: str, poll_interval: int = 8):
        self.address = address
        self.pubkey_hex = pubkey_hex
        self.session = requests.Session()
        self.poll_interval = poll_interval
        self.session.headers.update({"User-Agent": "simple-midnight-miner/1.0"})

    def get_terms(self, version="1-0"):
        r = self.session.get(f"{API_BASE}/TandC/{version}", timeout=15)
        r.raise_for_status()
        return r.json()

    def register(self, signature: str):
        url = f"{API_BASE}/register/{self.address}/{signature}/{self.pubkey_hex}"
        r = self.session.post(url, timeout=20)
        r.raise_for_status()
        return r.json()

    def get_challenge(self):
        r = self.session.get(f"{API_BASE}/challenge", timeout=20)
        r.raise_for_status()
        return r.json()

    def submit_solution(self, challenge_id: str, nonce_hex: str):
        url = f"{API_BASE}/solution/{self.address}/{challenge_id}/{nonce_hex}"
        r = self.session.post(url, timeout=20)
        r.raise_for_status()
        return r.json()

    # Temporary simplified POW (to be replaced with AshMaize)
    def solve(self, challenge: dict) -> str:
        difficulty = int(challenge["difficulty"], 16)
        base = (
            challenge.get("no_pre_mine", "")
            + str(challenge.get("no_pre_mine_hour", ""))
            + self.address
        ).encode()
        nonce = 0
        while True:
            nonce_bytes = nonce.to_bytes(8, "big", signed=False)
            h = hashlib.sha256(base + nonce_bytes).digest()
            prefix = int.from_bytes(h[:4], "big")
            if (prefix & difficulty) == 0:
                return binascii.hexlify(nonce_bytes).decode()
            nonce += 1
            if nonce % 200000 == 0:
                print(f"Tried {nonce:,} nonces...")
