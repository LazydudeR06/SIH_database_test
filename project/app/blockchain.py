import json, hashlib
from web3 import Web3

# --- Connect to Sepolia ---
INFURA_URL = "https://sepolia.infura.io/v3/YOUR_INFURA_PROJECT_ID"
PRIVATE_KEY = "0xYOUR_PRIVATE_KEY"
ACCOUNT = Web3(Web3.HTTPProvider(INFURA_URL)).eth.account.from_key(PRIVATE_KEY)
CONTRACT_ADDRESS = "0xYourDeployedContract"

w3 = Web3(Web3.HTTPProvider(INFURA_URL))

with open("backend/DocumentRegistry.json") as f:
    ABI = json.load(f)

contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI)

def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()

def store_hash_on_chain(doc_hash_hex: str) -> str:
    doc_hash_bytes = w3.to_bytes(hexstr=doc_hash_hex)
    nonce = w3.eth.get_transaction_count(ACCOUNT.address)
    tx = contract.functions.storeHash(doc_hash_bytes).build_transaction({
        "from": ACCOUNT.address,
        "nonce": nonce,
        "gas": 200000,
        "gasPrice": w3.to_wei("10", "gwei")
    })
    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return w3.to_hex(tx_hash)
