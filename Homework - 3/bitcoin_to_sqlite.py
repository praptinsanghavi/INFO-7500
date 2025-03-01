import modal
from modal import App, Volume, Secret
import os
import requests
import sqlite3
import json
import time
from typing import Dict, Any
import time
import logging

app = App(name="bitcoin-block-explorer")  # Use modal.App



# Define the volume and Docker image
volume = Volume.from_name("chongchen-bitcoin-data", create_if_missing=True)
bitcoin_image = modal.Image.debian_slim().pip_install("requests")

class BitcoinRPC:
    """Handles RPC communication with Bitcoin node via Chainstack"""
    def __init__(self):
        self.rpc_username = os.environ["RPC_USERNAME"]
        self.rpc_password = os.environ["RPC_PASSWORD"]
        self.rpc_host = os.environ["RPC_HOST"]
        self.rpc_port = os.environ["RPC_PORT"]
        self.rpc_path = os.environ["RPC_PATH"]
        self.rpc_endpoint = f"https://{self.rpc_host}:{self.rpc_port}{self.rpc_path}"
        self.auth = (self.rpc_username, self.rpc_password)

    def make_rpc_call(self, method: str, params: list) -> Dict[str, Any]:
        """Execute JSON-RPC call"""
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 1
        }
        try:
            response = requests.post(
                self.rpc_endpoint,
                auth=self.auth,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"RPC Error: {e}")
            raise

    def get_block_count(self) -> int:
        """Fetch current blockchain height"""
        resp = self.make_rpc_call("getblockcount", [])
        return resp["result"]

    def get_block_hash(self, height: int) -> str:
        """Get block hash by height"""
        resp = self.make_rpc_call("getblockhash", [height])
        return resp["result"]

    def get_block(self, block_hash: str) -> Dict:
        """Retrieve block data with transactions"""
        resp = self.make_rpc_call("getblock", [block_hash, 2])
        return resp["result"]

def get_db_connection():
    """Connect to SQLite database in Modal Volume"""
    return sqlite3.connect('/data/bitcoin.db')

def init_db():
    """Initialize database schema if not exists"""
    with get_db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS block (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hash VARCHAR(255) NOT NULL,
                confirmations INTEGER NOT NULL,
                height INTEGER NOT NULL,
                version INTEGER NOT NULL,
                versionHex VARCHAR(255) NOT NULL,
                merkleroot VARCHAR(255) NOT NULL,
                time INTEGER NOT NULL,
                mediantime INTEGER NOT NULL,
                nonce INTEGER NOT NULL,
                bits VARCHAR(255) NOT NULL,
                difficulty REAL NOT NULL,
                chainwork VARCHAR(255) NOT NULL,
                nTx INTEGER NOT NULL,
                previousblockhash VARCHAR(255) NOT NULL,
                nextblockhash VARCHAR(255) NOT NULL,
                strippedsize INTEGER NOT NULL,
                size INTEGER NOT NULL,
                weight INTEGER NOT NULL,
                tx JSON NOT NULL
            );
        """)
        conn.commit()

def get_max_height() -> int:
    """Get the highest block height from the database"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(height) AS max_height FROM block")
        row = cursor.fetchone()
        return row[0] if row[0] is not None else -1

def save_block(block_data: Dict):
    """Save block to database and Volume"""

    # Debug: Print Block Data
    print(f"📌 Attempting to save block {block_data['height']} - Hash: {block_data['hash']}")

    try:
        # Connect to SQLite
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Avoid Duplicate Insertion
            cursor.execute("SELECT COUNT(*) FROM block WHERE hash = ?", (block_data['hash'],))
            if cursor.fetchone()[0] > 0:
                print(f"⚠️ Block {block_data['height']} already exists. Skipping insertion.")
                return

            # Handle JSON Encoding Issues
            tx_data = json.dumps(block_data.get('tx', []))  # Default to empty list

            # Insert into SQLite
            cursor.execute("""
                INSERT INTO block (
                    hash, confirmations, height, version, versionHex, merkleroot,
                    time, mediantime, nonce, bits, difficulty, chainwork, nTx,
                    previousblockhash, nextblockhash, strippedsize, size, weight, tx
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                block_data['hash'],
                block_data.get('confirmations', 0),
                block_data['height'],
                block_data['version'],
                block_data['versionHex'],
                block_data['merkleroot'],
                block_data['time'],
                block_data.get('mediantime', block_data['time']),
                block_data['nonce'],
                block_data['bits'],
                block_data['difficulty'],
                block_data['chainwork'],
                block_data['nTx'],
                block_data.get('previousblockhash', 'UNKNOWN'),  # Handle missing previous block
                block_data.get('nextblockhash', 'UNKNOWN'),  # Handle missing next block
                block_data['strippedsize'],
                block_data['size'],
                block_data['weight'],
                tx_data  # Fixed JSON serialization
            ))

            conn.commit()

        # Save JSON to Volume
        block_dir = "/data/blocks"
        os.makedirs(block_dir, exist_ok=True)
        with open(f"{block_dir}/block_{block_data['height']}.json", 'w') as f:
            json.dump(block_data, f)

        print(f"✅ Block {block_data['height']} saved successfully.")

    except Exception as e:
        print(f"❌ Error saving block {block_data['height']}: {e}")


#@app.function(
 #   volumes={"/data": volume},
 #   image=bitcoin_image,
 #   secrets=[Secret.from_name("prapti-bitcoin-rpcauth")],
 #   timeout=86400  # Extend timeout for long syncing
#)

@app.function(secrets=[modal.Secret.from_name("prapti-bitcoin-rpcauth")])
def some_function():
    os.getenv("RPC_USERNAME")
    os.getenv("RPC_PASSWORD")
    os.getenv("RPC_HOST")
    os.getenv("RPC_PORT")

def sync_blocks():
    """Main function to sync Bitcoin blocks continuously into SQLite."""
    init_db()
    rpc = BitcoinRPC()

    # Setup logging for better debugging
    logging.basicConfig(filename="block_sync.log", level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")

    retry_attempts = 3  # Maximum retries per block
    sleep_time = 10  # Initial sleep time for retries
    stop_on_fail = False  # If True, stop syncing after a failure

    while True:
        try:
            current_height = rpc.get_block_count()
            max_synced = get_max_height()

            if max_synced >= current_height:
                print("✅ All blocks are up-to-date. Sleeping for 10 minutes...")
                logging.info("All blocks synced. Sleeping for 10 minutes.")
                time.sleep(600)  # Sleep for 10 minutes
                continue

            print(f"🚀 Syncing blocks {max_synced + 1} to {current_height}...")
            logging.info(f"Starting block sync from {max_synced + 1} to {current_height}")

            for height in range(max_synced + 1, current_height + 1):
                attempt = 0
                while attempt < retry_attempts:
                    try:
                        # Fetch block data
                        block_hash = rpc.get_block_hash(height)
                        block_data = rpc.get_block(block_hash)
                        
                        # Save to database
                        save_block(block_data)
                        print(f"✅ Block {height} synced successfully.")
                        logging.info(f"Block {height} synced successfully.")

                        if height % 10 == 0:
                            print(f"📊 Progress: {height}/{current_height} blocks synced.")

                        break  # Exit retry loop on success

                    except Exception as e:
                        attempt += 1
                        print(f"❌ Error syncing block {height}: {e} (Attempt {attempt}/{retry_attempts})")
                        logging.error(f"Error syncing block {height}: {e} (Attempt {attempt}/{retry_attempts})")

                        if attempt == retry_attempts:
                            print(f"⚠️ Max retries reached for block {height}. Skipping...")
                            logging.warning(f"Max retries reached for block {height}. Skipping...")
                            if stop_on_fail:
                                return  # Exit the function if a failure occurs

                        time.sleep(sleep_time * attempt)  # Exponential backoff

        except Exception as e:
            print(f"❌ Critical failure: {e}")
            logging.critical(f"Critical failure: {e}")
            time.sleep(600)  # Sleep for 10 minutes before retrying

if __name__ == "__main__":
    with app.run():
        sync_blocks