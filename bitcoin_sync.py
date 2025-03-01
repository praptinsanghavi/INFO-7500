import modal # type: ignore

# Create a Modal Stub (like a function registry)
stub = modal.Stub("bitcoin-sync")

# Define the volume that stores blockchain data
bitcoin_volume = modal.Volume.persisted("bitcoin-data")

# Function to start bitcoind inside Modal
@stub.function(
    cpu=4, memory=16, timeout=86400, volumes={"/data": bitcoin_volume},
    image=modal.Image.debian_slim().pip_install("requests")
)
def run_bitcoind():
    import subprocess
    import time

    # Start the Bitcoin daemon with persistent data
    process = subprocess.Popen([
        "bitcoind",
        "-datadir=/data",
        "-conf=/data/bitcoin.conf"
    ])

    # Keep checking blockchain sync progress
    while True:
        time.sleep(600)  # Wait 10 minutes before checking again
        subprocess.run(["bitcoin-cli", "-datadir=/data", "getblockchaininfo"])

# Function to check latest block count
@stub.function()
def check_blockchain_sync():
    import subprocess
    result = subprocess.run(["bitcoin-cli", "-datadir=/data", "getblockcount"], capture_output=True, text=True)
    print("Current Block Count:", result.stdout.strip())

# Run the sync
if __name__ == "__main__":
    stub.run(run_bitcoind)
