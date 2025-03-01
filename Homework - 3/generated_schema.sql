PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS block (hash TEXT, confirmations INTEGER, height INTEGER, version INTEGER, versionhex TEXT, merkleroot TEXT, time INTEGER, mediantime INTEGER, nonce INTEGER, bits TEXT, difficulty REAL, chainwork TEXT, ntx INTEGER, previousblockhash TEXT, nextblockhash TEXT, strippedsize INTEGER, size INTEGER, weight INTEGER);

CREATE TABLE IF NOT EXISTS transactions (txid TEXT, block_hash TEXT, version INTEGER, locktime INTEGER, size INTEGER, weight INTEGER, amount REAL, fee REAL);


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



CREATE TABLE IF NOT EXISTS tx_output (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    txid TEXT NOT NULL,
    output_index INTEGER NOT NULL,
    value REAL NOT NULL,
    script_pubkey TEXT,
    FOREIGN KEY (txid) REFERENCES transactions(txid) ON DELETE CASCADE
);
