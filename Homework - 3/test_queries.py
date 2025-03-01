import unittest
import sqlite3
from query_modal_db import extract_schema, generate_sql_query
import os

# Define the database path
DB_PATH = "blockchain.db"

def run_sql_query(db_path, sql_query):
    """
    Executes the generated SQL query on the SQLite database and returns the results.
    """
    if not os.path.exists(db_path):
        return "Error: Database file not found."
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        conn.commit()
    except sqlite3.Error as e:
        rows = f"Error executing SQL: {e}"
    conn.close()
    return rows

class TestSQLGeneration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Extract database schema before running tests."""
        if os.path.exists(DB_PATH):
            cls.schema = extract_schema(DB_PATH)
        else:
            cls.schema = ""

    def test_query_block_count(self):
        """Test SQL generation and execution for counting blocks."""
        nl_query = "How many blocks are in the database?"
        sql_query = generate_sql_query(nl_query, self.schema)
        self.assertIn("SELECT", sql_query.upper())
        self.assertIn("COUNT", sql_query.upper())
        actual_result = run_sql_query(DB_PATH, sql_query)
        self.assertEqual(actual_result, [(2,)])  # Expected based on sample DB

    def test_query_latest_block(self):
        """Test SQL generation and execution for latest block hash."""
        nl_query = "What is the hash of the latest block?"
        sql_query = generate_sql_query(nl_query, self.schema)
        self.assertIn("hash", sql_query.lower())
        self.assertIn("ORDER BY", sql_query.upper())
        actual_result = run_sql_query(DB_PATH, sql_query)
        self.assertEqual(actual_result, [("0000000000000000000b1c2d3e4f5g6h7i8j9k0l",)])

    def test_query_largest_transaction(self):
        """Test SQL generation for finding the largest transaction."""
        nl_query = "What was the largest transaction in block 407048?"
        sql_query = generate_sql_query(nl_query, self.schema)
        self.assertIn("ORDER BY", sql_query.upper())
        self.assertIn("LIMIT 1", sql_query.upper())
        actual_result = run_sql_query(DB_PATH, sql_query)  # Execute query
        self.assertIsInstance(actual_result, list)  # Validate result type

    
    def test_query_block_by_height(self):
        """Test SQL generation and execution for retrieving block details by height."""
        nl_query = "What is the hash of block 500000?"
        sql_query = generate_sql_query(nl_query, self.schema)
        self.assertIn("WHERE", sql_query.upper())
        self.assertIn("height", sql_query.lower())
        actual_result = run_sql_query(DB_PATH, sql_query)
        self.assertEqual(actual_result, [("0000000000000000000a1b2c3d4e5f6g7h8i9j0k",)])

    def test_query_transaction_count(self):
        """Test SQL generation for counting transactions."""
        nl_query = "How many transactions are in the database?"
        sql_query = generate_sql_query(nl_query, self.schema)
        self.assertIn("COUNT", sql_query.upper())
        self.assertIn("transactions", sql_query.lower())

    def test_query_transaction_in_block(self):
        """Test SQL generation for listing transactions in a specific block."""
        nl_query = "List all transactions in block 407048."
        sql_query = generate_sql_query(nl_query, self.schema)
        self.assertIn("WHERE", sql_query.upper())
        self.assertIn("block_hash", sql_query.lower())

    def test_query_block_difficulty(self):
        """Test SQL generation for finding the highest difficulty block."""
        nl_query = "Which block has the highest difficulty?"
        sql_query = generate_sql_query(nl_query, self.schema)
        self.assertIn("ORDER BY", sql_query.upper())
        self.assertIn("difficulty", sql_query.lower())

    def test_query_block_timestamp(self):
        """Test SQL generation for finding the timestamp of a block."""
        nl_query = "What is the timestamp of block 600000?"
        sql_query = generate_sql_query(nl_query, self.schema)
        self.assertIn("time", sql_query.lower())
        self.assertIn("height", sql_query.lower())

    def test_query_top_blocks(self):
        """Test SQL generation for listing the top 5 blocks with most transactions."""
        nl_query = "Which 5 blocks have the most transactions?"
        sql_query = generate_sql_query(nl_query, self.schema)
        self.assertIn("ORDER BY", sql_query.upper())
        self.assertIn("LIMIT 5", sql_query.upper())
    
    def test_query_total_transaction_value(self):
        """Test SQL generation and execution for total transaction value."""
        nl_query = "What is the total value of all transactions?"
        sql_query = generate_sql_query(nl_query, self.schema)
        self.assertIn("SUM", sql_query.upper())
        actual_result = run_sql_query(DB_PATH, sql_query)
        self.assertEqual(actual_result, [(8.25,)])  # Expected from test data

class TestEdgeCases(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Extract database schema before running tests."""
        cls.schema = extract_schema(DB_PATH)

    def test_ambiguous_query(self):
        """Test ambiguous natural language query."""
        nl_query = "What is the biggest block?"
        sql_query = generate_sql_query(nl_query, self.schema)
        self.assertTrue(("size" in sql_query.lower() or "ntx" in sql_query.lower()),
                        "Generated SQL should clarify whether it's by size or transaction count.")

    def test_incorrect_syntax(self):
        """Test incorrect SQL query handling."""
        nl_query = "Give me the total transactions from the largest block."
        sql_query = generate_sql_query(nl_query, self.schema)
        try:
            run_sql_query(DB_PATH, sql_query)  # Execute query
        except sqlite3.Error as e:
            self.assertIn("syntax", str(e).lower(), "Should detect syntax error if query is invalid.")

    def test_query_nonexistent_block(self):
        """Test SQL query for a non-existent block."""
        nl_query = "What is the hash of block 999999999?"
        sql_query = generate_sql_query(nl_query, self.schema)
        result = run_sql_query(DB_PATH, sql_query)
        print(f"\n🔍 Debugging test_query_nonexistent_block - Query Results: {result}")
        self.assertEqual(len(result), 0, f"Query should return no results for a block that does not exist. Returned: {len(result)} results.")

    # --- HARD TEST CASES ---
    def test_hard_case_1_highest_transaction_wallet(self):
        """Test failure case: Find the wallet with highest total transaction value, considering difficulty > 18000000000000."""
        nl_query = "Find the wallet address with the highest total transaction value, but only consider transactions made in blocks with difficulty above 18000000000000."
        incorrect_sql = generate_sql_query(nl_query, self.schema)
        expected_sql = """
            SELECT a.address, SUM(t.value) AS total_value 
            FROM transactions t
            JOIN addresses a ON t.txid = a.txid
            JOIN blocks b ON t.block_height = b.height
            WHERE b.difficulty > 18000000000000
            GROUP BY a.address
            ORDER BY total_value DESC
            LIMIT 1;
        """
        expected_result = [("3ExampleHighValueAddr", 50.75)]
        incorrect_result = run_sql_query(DB_PATH, incorrect_sql)

        self.assertNotEqual(incorrect_sql.strip(), expected_sql.strip(), "System should generate incorrect SQL.")
        self.assertNotEqual(incorrect_result, expected_result, "System should fail to return correct results.")

    def test_hard_case_2_highest_transaction_per_block(self):
        """Test failure case: Find the highest transaction value per block using window functions."""
        nl_query = "For each block, find the transaction with the highest value and return the block height, transaction ID, and value."
        incorrect_sql = generate_sql_query(nl_query, self.schema)
        expected_sql = """
            SELECT block_height, txid, value FROM (
                SELECT block_height, txid, value,
                    RANK() OVER (PARTITION BY block_height ORDER BY value DESC) as r
                FROM transactions
            ) ranked
            WHERE r = 1;
        """
        expected_result = [(500000, "txid5000", 12.5), (600000, "txid6000", 8.75)]
        incorrect_result = run_sql_query(DB_PATH, incorrect_sql)

        self.assertNotEqual(incorrect_sql.strip(), expected_sql.strip(), "System should generate incorrect SQL.")
        self.assertNotEqual(incorrect_result, expected_result, "System should fail to return correct results.")

    def test_hard_case_3_recursive_ancestor_blocks(self):
        """Test failure case: Find all ancestor blocks for block 600000 recursively back to genesis block."""
        nl_query = "Find all ancestor blocks for block 600000, recursively traversing back to the genesis block."
        incorrect_sql = generate_sql_query(nl_query, self.schema)
        expected_sql = """
            WITH RECURSIVE ancestors AS (
                SELECT height, hash FROM blocks WHERE height = 600000
                UNION ALL
                SELECT b.height, b.hash FROM blocks b
                JOIN ancestors a ON b.height = a.height - 1
            )
            SELECT * FROM ancestors;
        """
        expected_result = [(600000, "0000000000000000000b1c2d3e4f5g6h7i8j9k0l"), (599999, "0000000000000000000a1b2c3d4e5f6g7h8i9j0k")]
        incorrect_result = run_sql_query(DB_PATH, incorrect_sql)

        self.assertNotEqual(incorrect_sql.strip(), expected_sql.strip(), "System should generate incorrect SQL.")
        self.assertNotEqual(incorrect_result, expected_result, "System should fail to return correct results.")

if __name__ == "__main__":
    unittest.main()