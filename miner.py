from wallet import WalletManager
from api import MidnightMiner
import time
import json
import os


def main():
    print("=== Midnight Miner (Lace Wallet Mode) ===")

    wm = WalletManager()
    wallets = wm.list_wallets()

    print("\nAvailable wallets:")
    for i, w in enumerate(wallets):
        print(f"[{i}] {w['name']} - {w['address'][:20]}...")

    index = int(input("\nSelect wallet index: ") or 0)
    wallet = wm.get_wallet(index)

    address = wallet["address"]
    pubkey_hex = wallet["pubkey_hex"]

    miner = MidnightMiner(address, pubkey_hex)

    # ✅ Step 1 — Load saved signatures
    sig_file = "signatures.json"
    signature_hex = None

    if os.path.exists(sig_file):
        with open(sig_file, "r", encoding="utf-8") as f:
            sigs = json.load(f)
            signature_hex = sigs.get(address)

    if not signature_hex:
        # Ask user only if signature is not stored
        terms = miner.get_terms()
        message = terms.get("message", "")
        print("Fetched T&C message for signing.\n")
        print("⚠️  Please sign this message using your Lace wallet manually:\n")
        print(message)
        print("\nThen paste the signature below.\n")
        signature_hex = input("Enter your signature (hex): ").strip()

        # Save it for future runs
        sigs = {}
        if os.path.exists(sig_file):
            with open(sig_file, "r", encoding="utf-8") as f:
                try:
                    sigs = json.load(f)
                except Exception:
                    sigs = {}
        sigs[address] = signature_hex
        with open(sig_file, "w", encoding="utf-8") as f:
            json.dump(sigs, f, indent=2)
        print(f"Saved signature for {address} in {sig_file}")

    # ✅ Step 2 — Register once using saved signature
    try:
        reg = miner.register(signature_hex)
        print("Registered successfully:", reg)
    except Exception as e:
        print("Registration failed:", e)
        return

    # ✅ Step 3 — Start mining loop
    print("\nStarting mining loop... (Ctrl+C to stop)\n")

    while True:
        try:
            ch = miner.get_challenge()
            print("New challenge:", ch.get("challenge_id"), "diff:", ch.get("difficulty"))
            nonce_hex = miner.solve(ch)
            print("Found nonce:", nonce_hex)
            res = miner.submit_solution(ch["challenge_id"], nonce_hex)
            print("Result:", res)
        except KeyboardInterrupt:
            print("Stopped by user.")
            break
        except Exception as e:
            print("Error:", e)
            time.sleep(miner.poll_interval)


if __name__ == "__main__":
    main()
