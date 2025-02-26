import os
import requests
import sqlite3
from time import sleep
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class BitcoinRPC:
    """
    This class communicates with the Bitcoin Core node via RPC.
    It sends JSON-RPC requests and returns the results.
    """
#    def __init__(self):
#        self.rpc_user = os.getenv("RPC_USERNAME")
#        self.rpc_password = os.getenv("RPC_PASSWORD")
#        self.rpc_host = os.getenv("RPC_HOST", "127.0.0.1")
#        self.rpc_port = os.getenv("RPC_PORT", "8332")
#        self.rpc_url = f"http://{self.rpc_host}:{self.rpc_port}"

    def __init__(self):
        self.rpc_user = os.getenv("RPC_USERNAME")
        self.rpc_password = os.getenv("RPC_PASSWORD")
        self.rpc_host = os.getenv("RPC_HOST", "127.0.0.1")
        self.rpc_port = os.getenv("RPC_PORT", "8332")
        print("Loaded RPC credentials:")
        print("User:", self.rpc_user)
        print("Password:", self.rpc_password)
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

def update_database():
    """
    Fetch the latest block and its transactions from Bitcoin Core,
    then update the SQLite database (blockchain.db) with the block and transaction data.
    """
    # Connect to the SQLite database (it should already have been created using schema.sql)
    conn = sqlite3.connect("blockchain.db")
    cursor = conn.cursor()

    rpc = BitcoinRPC()

    # Fetch the best (latest) block hash.
    best_block_hash = rpc.call("getbestblockhash")
    if not best_block_hash:
        print("Failed to retrieve the best block hash.")
        conn.close()
        return

    print("Latest block hash:", best_block_hash)

    # Fetch detailed block data with verbosity=2.
    block_data = rpc.call("getblock", [best_block_hash, 2])
    if not block_data:
        print("Failed to retrieve detailed block data.")
        conn.close()
        return

    # Insert or update block data into the 'block' table.
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
        print("Block inserted/updated:", block_data["hash"])
    except Exception as e:
        print("Error inserting block data:", e)

    # Loop through the transactions in the block and update the 'transaction' table.
    # Assumes the transaction table has columns: txid, block_hash, version, locktime, size, weight
    transactions = block_data.get("tx", [])
    for tx in transactions:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO transaction (
                    txid, block_hash, version, locktime, size, weight
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                tx["txid"],
                block_data["hash"],  # associate this tx with the block's hash
                tx["version"],
                tx["locktime"],
                tx["size"],
                tx["weight"]
            ))
            print("Transaction inserted:", tx["txid"])
        except Exception as e:
            print("Error inserting transaction data for txid", tx.get("txid"), ":", e)

    conn.commit()
    conn.close()

def main():
    """
    Periodically update the database every 5 minutes.
    """
    while True:
        print("Starting update cycle...")
        update_database()
        print("Cycle complete. Waiting 5 minutes before next update...")
        sleep(300)  # Sleep for 300 seconds (5 minutes)

if __name__ == "__main__":
    main()
