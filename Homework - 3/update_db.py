import os
import requests
import sqlite3
import schedule
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class BitcoinRPC:
    """
    Communicates with the Bitcoin Core node via JSON-RPC.
    Sends RPC requests and returns the results.
    """

    def __init__(self):
        self.rpc_user = os.getenv("RPC_USERNAME")
        self.rpc_password = os.getenv("RPC_PASSWORD")
        self.rpc_host = os.getenv("RPC_HOST", "127.0.0.1")
        self.rpc_port = os.getenv("RPC_PORT", "8332")
        self.rpc_url = f"http://{self.rpc_host}:{self.rpc_port}"
    
    def call(self, method, params=[]):
        payload = {
            "jsonrpc": "1.0",
            "id": "pythonclient",
            "method": method,
            "params": params
        }
        try:
            response = requests.post(
                self.rpc_url,
                auth=(self.rpc_user, self.rpc_password),
                json=payload
            )
            response.raise_for_status()
            return response.json()["result"]
        except Exception as e:
            print(f"RPC call error for method {method}: {e}")
            return None

def insert_block(cursor, block_data):
    """
    Inserts a new block into the 'block' table.
    Uses `INSERT OR IGNORE` to avoid duplicate entries.
    """
    try:
        cursor.execute("""
            INSERT OR IGNORE INTO block (
                hash, confirmations, height, version, versionhex, merkleroot,
                time, mediantime, nonce, bits, difficulty, chainwork, ntx,
                previousblockhash, nextblockhash, strippedsize, size, weight
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            block_data["hash"],
            block_data["confirmations"],
            block_data["height"],
            block_data["version"],
            block_data["versionHex"],
            block_data["merkleroot"],
            block_data["time"],
            block_data["mediantime"],
            block_data["nonce"],
            block_data["bits"],
            block_data["difficulty"],
            block_data["chainwork"],
            block_data["nTx"],
            block_data.get("previousblockhash"),
            block_data.get("nextblockhash"),
            block_data["strippedsize"],
            block_data["size"],
            block_data["weight"]
        ))
        print(f"✅ Block inserted: {block_data['hash']}")
    except Exception as e:
        print("❌ Error inserting block:", e)

def insert_transaction(cursor, tx, block_hash):
    """
    Inserts a transaction into the 'transactions' table.
    Uses `INSERT OR IGNORE` to prevent duplicate entries.
    """
    try:
        cursor.execute("""
            INSERT OR IGNORE INTO transactions (
                txid, block_hash, version, locktime, size, weight, amount, fee
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            tx["txid"],
            block_hash,
            tx["version"],
            tx["locktime"],
            tx["size"],
            tx["weight"],
            tx.get("amount", 0),  # Default to 0 if missing
            tx.get("fee", 0)  # Default to 0 if missing
        ))
        print(f"✅ Transaction inserted: {tx['txid']}")
    except Exception as e:
        print(f"❌ Error inserting transaction {tx['txid']}: {e}")

def insert_tx_inputs(cursor, tx):
    """
    Inserts transaction inputs (`vin`) into the 'tx_input' table.
    """
    for idx, vin in enumerate(tx.get("vin", [])):
        try:
            cursor.execute("""
                INSERT INTO tx_input (txid, input_index, prev_txid, prev_vout, script_sig, sequence)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                tx["txid"],
                idx,
                vin.get("txid"),  # Previous transaction ID
                vin.get("vout"),  # Output index of previous tx
                vin.get("scriptSig", {}).get("hex"),  # Script signature
                vin.get("sequence", 0)
            ))
        except Exception as e:
            print(f"❌ Error inserting tx_input for {tx['txid']}: {e}")

def insert_tx_outputs(cursor, tx):
    """
    Inserts transaction outputs (`vout`) into the 'tx_output' table.
    """
    for idx, vout in enumerate(tx.get("vout", [])):
        try:
            cursor.execute("""
                INSERT INTO tx_output (txid, output_index, value, script_pubkey)
                VALUES (?, ?, ?, ?)
            """, (
                tx["txid"],
                idx,
                vout["value"],
                vout["scriptPubKey"]["hex"]
            ))
        except Exception as e:
            print(f"❌ Error inserting tx_output for {tx['txid']}: {e}")

def update_database():
    """
    Fetches the latest block and its transactions from Bitcoin Core,
    then updates the SQLite database (`blockchain.db`).
    """
    conn = sqlite3.connect("blockchain.db")
    cursor = conn.cursor()
    rpc = BitcoinRPC()

    # Fetch the latest block hash
    latest_block_hash = rpc.call("getbestblockhash")
    if not latest_block_hash:
        print("❌ Failed to retrieve the latest block hash.")
        conn.close()
        return

    print(f"🔄 Fetching block: {latest_block_hash}")

    # Fetch detailed block data
    block_data = rpc.call("getblock", [latest_block_hash, 2])
    if not block_data:
        print("❌ Failed to retrieve block data.")
        conn.close()
        return

    try:
        # Start transaction
        cursor.execute("BEGIN TRANSACTION")

        # Insert block data
        insert_block(cursor, block_data)

        # Insert transactions
        for tx in block_data["tx"]:
            insert_transaction(cursor, tx, block_data["hash"])
            insert_tx_inputs(cursor, tx)
            insert_tx_outputs(cursor, tx)

        # Commit transaction
        conn.commit()
        print(f"✅ Database updated with block {block_data['height']}")

    except Exception as e:
        conn.rollback()  # Rollback in case of failure
        print("❌ Error updating database:", e)

    finally:
        conn.close()

def run_scheduler():
    """
    Runs the update function every 5 minutes.
    """
    schedule.every(5).minutes.do(update_database)

    print("⏳ Blockchain sync started. Updating every 5 minutes...")

    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    run_scheduler()
