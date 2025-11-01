from wallet import WalletManager
from api import MidnightMiner
from pycardano import Network, PaymentSigningKey
import cbor2
import time

def sign_cip30(payment_key, address: str, message: str) -> str:
    msg_bytes = message.encode("utf-8")

    # Protected header (algorithm)
    protected = cbor2.dumps({1: -8})
    # Unprotected header (address)
    unprotected = {400: address.encode("utf-8")}

    # The Sig_structure context, per CIP-8
    sig_structure = [
        "Signature1",
        protected,
        b"",
        msg_bytes,
    ]
    to_sign = cbor2.dumps(sig_structure)
    signature = payment_key.sign(to_sign)

    cose_sign1 = [protected, unprotected, msg_bytes, signature]
    return cbor2.dumps(cose_sign1).hex()

def main():
    print("=== Midnight Miner (No Lace) ===")

    # Use TESTNET until Scavenger switches to mainnet (avoid network mismatch errors)
    network = Network.TESTNET
    wm = WalletManager(network=network)
    wm.create_or_load_wallet()

    address = wm.get_address()
    pubkey_hex = wm.get_pubkey_hex()
    payment_key = wm.get_payment_key()
    print(f"Address: {address}\nPubkey: {pubkey_hex[:20]}...\n")

    miner = MidnightMiner(address, pubkey_hex)

    # Step 1: Get Terms & Conditions
    terms = miner.get_terms()
    message = terms.get("message", "")
    print("Fetched T&C message for signing...")

    # Step 2: CIP-30-compliant signature
    signature_hex = sign_cip30(payment_key, address, message)
    print("Signed message locally (CIP-30).")

    # Step 3: Register
    try:
        print(f"\nSignature (hex, first 80): {signature_hex[:80]}...\n")
        reg = miner.register(signature_hex)
        print("Registered successfully:", reg)
    except Exception as e:
        print("Registration failed:", e)
        return

    # Step 4: Start mining loop
    print("\nStarting mining loop... (Ctrl+C to stop)\n")
    while True:
        try:
            ch = miner.get_challenge()
            print("New challenge:", ch.get("challenge", {}).get("challenge_id"), "diff:", ch.get("challenge", {}).get("difficulty"))
            nonce_hex = miner.solve(ch.get("challenge", {}))
            print("Found nonce:", nonce_hex)
            res = miner.submit_solution(ch["challenge"]["challenge_id"], nonce_hex)
            print("Result:", res)
        except KeyboardInterrupt:
            print("Stopped by user.")
            break
        except Exception as e:
            print("Error:", e)
            time.sleep(miner.poll_interval)

if __name__ == "__main__":
    main()
