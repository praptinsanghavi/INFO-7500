import unittest
import sqlite3
from query_modal_db import extract_schema, generate_sql_query

# Define the database path
DB_PATH = "blockchain.db"

def run_sql_query(db_path, sql_query):
    """
    Executes the generated SQL query on the SQLite database and returns the results.
    """
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
        cls.schema = extract_schema(DB_PATH)

    def test_query_block_count(self):
        """Test SQL generation for counting blocks."""
        nl_query = "How many blocks are in the database?"
        sql_query = generate_sql_query(nl_query, self.schema)
        self.assertIn("SELECT", sql_query.upper())
        self.assertIn("COUNT", sql_query.upper())

    def test_query_latest_block(self):
        """Test SQL generation for getting the latest block hash."""
        nl_query = "What is the hash of the latest block?"
        sql_query = generate_sql_query(nl_query, self.schema)
        self.assertIn("hash", sql_query.lower())
        self.assertIn("ORDER BY", sql_query.upper())

    def test_query_largest_transaction(self):
        """Test SQL generation for finding the largest transaction."""
        nl_query = "What was the largest transaction in block 407048?"
        sql_query = generate_sql_query(nl_query, self.schema)
        self.assertIn("ORDER BY", sql_query.upper())
        self.assertIn("LIMIT 1", sql_query.upper())

    def test_query_block_by_height(self):
        """Test SQL generation for finding a block by height."""
        nl_query = "What is the hash of block 500000?"
        sql_query = generate_sql_query(nl_query, self.schema)
        self.assertIn("WHERE", sql_query.upper())
        self.assertIn("height", sql_query.lower())

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
        """Test SQL generation for finding the total value of transactions."""
        nl_query = "What is the total value of all transactions in the database?"
        sql_query = generate_sql_query(nl_query, self.schema)
        self.assertIn("SUM", sql_query.upper())
        self.assertIn("value", sql_query.lower())

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


if __name__ == "__main__":
    unittest.main()
