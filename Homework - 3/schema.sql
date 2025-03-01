PRAGMA foreign_keys = ON;

-- Block Table: Stores all block-level data from the getblock RPC call.
CREATE TABLE IF NOT EXISTS block (
    hash VARCHAR(255) PRIMARY KEY,  -- Changed from id to hash as primary key
    confirmations INTEGER NOT NULL,
    height INTEGER NOT NULL,
    version INTEGER NOT NULL,
    versionhex VARCHAR(255) NOT NULL,
    merkleroot VARCHAR(255) NOT NULL,
    time INTEGER NOT NULL,
    mediantime INTEGER NOT NULL,
    nonce INTEGER NOT NULL,
    bits VARCHAR(255) NOT NULL,
    difficulty REAL NOT NULL,
    chainwork VARCHAR(255) NOT NULL,
    ntx INTEGER NOT NULL,
    previousblockhash VARCHAR(255),
    nextblockhash VARCHAR(255),
    strippedsize INTEGER NOT NULL,
    size INTEGER NOT NULL,
    weight INTEGER NOT NULL
);

-- Transaction Table: Stores individual transactions associated with blocks.
CREATE TABLE IF NOT EXISTS transactions (
    txid VARCHAR(255) PRIMARY KEY,
    block_hash VARCHAR(255) NOT NULL,
    version INTEGER NOT NULL,
    locktime INTEGER NOT NULL,
    size INTEGER NOT NULL,
    weight INTEGER NOT NULL,
    amount REAL NOT NULL,  -- Total transaction amount
    fee REAL NOT NULL,  -- Transaction fee
    FOREIGN KEY (block_hash) REFERENCES block(hash) ON DELETE CASCADE  -- Ensures integrity, Fixed reference
);

-- Transaction Inputs Table: Stores inputs for each transaction.
CREATE TABLE IF NOT EXISTS tx_input (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    txid VARCHAR(255) NOT NULL,
    input_index INTEGER NOT NULL,
    prev_txid VARCHAR(255),  -- Reference to previous transaction
    prev_vout INTEGER,
    script_sig TEXT,
    sequence INTEGER,
    FOREIGN KEY (txid) REFERENCES transactions(txid) ON DELETE CASCADE  -- Ensure deletion cascades
);

-- Transaction Outputs Table: Stores outputs for each transaction.
CREATE TABLE IF NOT EXISTS tx_output (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    txid VARCHAR(255) NOT NULL,
    output_index INTEGER NOT NULL,
    value REAL NOT NULL,  -- Transaction amount
    script_pubkey TEXT,
    FOREIGN KEY (txid) REFERENCES transactions(txid) ON DELETE CASCADE  -- Ensure deletion cascades, Fixed reference
);