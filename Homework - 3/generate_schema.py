import json

# Sample JSON response from `getblocks` RPC with verbosity=2
sample_json = {
    "hash": "00000000000000000008abcdef",
    "confirmations": 12345,
    "height": 758923,
    "version": 536870912,
    "versionhex": "00000002",
    "merkleroot": "3a5b...",
    "time": 1638748271,
    "mediantime": 1638748000,
    "nonce": 123456,
    "bits": "1a2b3c",
    "difficulty": 23.97,
    "chainwork": "000abc123...",
    "ntx": 5,
    "previousblockhash": "00000000000000000007...",
    "nextblockhash": "00000000000000000009...",
    "strippedsize": 999,
    "size": 1000,
    "weight": 4000,
    "tx": [
        {
            "txid": "abc123txid",
            "block_hash": "00000000000000000008abcdef",
            "version": 2,
            "locktime": 0,
            "size": 250,
            "weight": 1000,
            "amount": 0.25,
            "fee": 0.0001,
            "vin": [
                {"txid": "prevtxid123", "vout": 1, "scriptSig": "304502...", "sequence": 4294967295}
            ],
            "vout": [
                {"value": 0.25, "scriptPubKey": "76a914abcd1234ef567890..."}
            ]
        }
    ]
}

# Function to generate SQLite schema from JSON
def json_to_sql_schema(json_obj, table_name):
    sql_statements = []
    
    for key, value in json_obj.items():
        if isinstance(value, int):
            sql_type = "INTEGER"
        elif isinstance(value, float):
            sql_type = "REAL"
        elif isinstance(value, str):
            sql_type = "TEXT"
        elif isinstance(value, list):
            continue  # Skip arrays for now (handle separately)
        else:
            sql_type = "TEXT"

        sql_statements.append(f"{key} {sql_type}")

    return f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(sql_statements)});"

# Generate schema for `block` table
block_schema = json_to_sql_schema(sample_json, "block")

# Generate schema for `transactions` table
transaction_schema = json_to_sql_schema(sample_json["tx"][0], "transactions")

# Generate schema for `tx_input` (Transaction Inputs)
tx_input_schema = """
CREATE TABLE IF NOT EXISTS tx_input (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    txid TEXT NOT NULL,
    input_index INTEGER NOT NULL,
    prev_txid TEXT,
    prev_vout INTEGER,
    script_sig TEXT,
    sequence INTEGER,
    FOREIGN KEY (txid) REFERENCES transactions(txid) ON DELETE CASCADE
);
"""

# Generate schema for `tx_output` (Transaction Outputs)
tx_output_schema = """
CREATE TABLE IF NOT EXISTS tx_output (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    txid TEXT NOT NULL,
    output_index INTEGER NOT NULL,
    value REAL NOT NULL,
    script_pubkey TEXT,
    FOREIGN KEY (txid) REFERENCES transactions(txid) ON DELETE CASCADE
);
"""

# Save the generated schema to a file
with open("generated_schema.sql", "w") as f:
    f.write("PRAGMA foreign_keys = ON;\n\n")
    f.write(block_schema + "\n\n")
    f.write(transaction_schema + "\n\n")
    f.write(tx_input_schema + "\n\n")
    f.write(tx_output_schema)

# Print output for verification
print("✅ Auto-Generated SQL Schema:\n")
print(block_schema)
print("\n" + transaction_schema)
print("\n" + tx_input_schema)
print("\n" + tx_output_schema)
print("\n✅ Schema saved to `generated_schema.sql`")
