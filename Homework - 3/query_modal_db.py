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
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            print("⚠️ Warning: No tables found in the database.")
            return ""

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
    except sqlite3.Error as e:
        print(f"❌ Error: Unable to extract schema. SQLite error: {e}")
        return ""

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

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a SQL expert that only returns SQL queries."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        sql_query = response.choices[0].message.content

        # ✅ Remove unwanted markdown formatting
        sql_query = sql_query.strip().strip("```sql").strip("```")

        # ✅ Validate OpenAI output to ensure it's a proper SQL query
        if not sql_query.lower().startswith(("select", "insert", "update", "delete")):
            print("⚠️ Warning: The generated response does not appear to be a valid SQL query.")
            print("Returned Output:\n", sql_query)
            return ""

        return sql_query.strip()
    except Exception as e:
        print(f"❌ Error: Unable to generate SQL query. OpenAI API error: {e}")
        return ""

def main():
    # Get the database path and natural language query from the user
    db_path = input("Enter the absolute path to your SQLite database (e.g., blockchain.db): ").strip()

    # ✅ Enhanced Error Handling: Check if the database file exists
    if not os.path.exists(db_path):
        print("❌ Error: The provided database path does not exist. Please check and try again.")
        return  # Exit the function if the path is incorrect

    nl_query = input("Enter your natural language query: ").strip()

    # Extract the schema from the database
    schema = extract_schema(db_path)

    if not schema:
        print("❌ Error: No schema extracted. Cannot generate an SQL query.")
        return  # Exit if schema extraction failed

    print("\nExtracted Database Schema:\n")
    print(schema)

    # Generate the SQL query using the schema and natural language query
    sql_query = generate_sql_query(nl_query, schema)

    if not sql_query:
        print("❌ Error: No valid SQL query was generated.")
        return  # Exit if OpenAI failed to generate a proper query

    print("\nGenerated SQL Query:\n")
    print(sql_query)

if __name__ == "__main__":
    main()
