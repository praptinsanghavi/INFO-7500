import os
import sqlite3
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Ensure the API key is set
if OPENAI_API_KEY is None:
    raise ValueError("Error: OpenAI API key is missing. Set it in the .env file.")

# Create OpenAI client using API key
client = openai.OpenAI(api_key=OPENAI_API_KEY)

def extract_schema(db_path):
    """
    Connects to the SQLite database and extracts its schema.
    Returns a string describing all tables and columns.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    schema_description = ""
    for table in tables:
        table_name = table[0]
        schema_description += f"Table: {table_name}\n"
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()  # (cid, name, type, notnull, dflt_value, pk)
        for col in columns:
            schema_description += f"  - {col[1]} ({col[2]})\n"
        schema_description += "\n"
    conn.close()
    return schema_description

def generate_sql_query(nl_query, schema):
    """
    Uses the OpenAI API to convert a natural language query into an SQL query,
    given the database schema.
    """
    prompt = (
        "You are a SQL expert specializing in Bitcoin blockchain data. "
        "You are given the following SQLite database schema:\n\n"
        f"{schema}\n\n"
        "Translate the following natural language question into a correct SQL query. "
        "Always use ORDER BY for ranking queries instead of aggregation functions like MAX(). "
        "Return only the SQL query, with no explanations or markdown formatting.\n\n"
        f"Natural language query: {nl_query}"
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a SQL expert that only returns SQL queries."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    sql_query = response.choices[0].message.content

    # ✅ Fix: Remove unwanted markdown formatting
    sql_query = sql_query.strip().strip("```sql").strip("```")

    return sql_query.strip()

def main():
    # Get the database path and natural language query from the user
    db_path = input("Enter the absolute path to your SQLite database (e.g., blockchain.db): ").strip()
    nl_query = input("Enter your natural language query: ").strip()

    # Extract the schema from the database
    schema = extract_schema(db_path)
    print("\nExtracted Database Schema:\n")
    print(schema)

    # Generate the SQL query using the schema and natural language query
    sql_query = generate_sql_query(nl_query, schema)
    print("\nGenerated SQL Query:\n")
    print(sql_query)

if __name__ == "__main__":
    main()
