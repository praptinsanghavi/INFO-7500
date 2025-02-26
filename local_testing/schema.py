import sys
import json

def infer_sql_type(value):
    """
    Infer an SQL type based on the Python type of the JSON value.
    """
    if isinstance(value, int):
        return "INTEGER"
    elif isinstance(value, float):
        return "REAL"
    elif isinstance(value, str):
        # You can adjust this if you want TEXT for longer strings
        return "VARCHAR(255)"
    elif isinstance(value, bool):
        return "BOOLEAN"
    elif value is None:
        # When value is None, we default to TEXT.
        return "TEXT"
    elif isinstance(value, list):
        # Lists are skipped (to be handled separately)
        return None
    elif isinstance(value, dict):
        # For nested dictionaries, store as JSON string
        return "TEXT"
    else:
        return "TEXT"

def generate_table_schema(table_name, sample_data, skip_keys=[]):
    """
    Generate a CREATE TABLE statement for a table with the given name,
    based on the keys in sample_data. Keys listed in skip_keys are omitted.
    """
    schema_lines = []
    for key, value in sample_data.items():
        if key in skip_keys:
            continue
        sql_type = infer_sql_type(value)
        if sql_type is None:
            # Skip fields that are lists (like "tx" in the block JSON)
            continue
        # Here we assume all columns are NOT NULL. You might adjust this as needed.
        schema_lines.append(f"    {key} {sql_type} NOT NULL")
    
    # Join the column definitions with commas.
    columns = ",\n".join(schema_lines)
    create_statement = f"CREATE TABLE IF NOT EXISTS {table_name} (\n{columns}\n);"
    return create_statement

def main():
    if len(sys.argv) < 2:
        print("Usage: python schema_autogen.py <sample_getblock.json>")
        sys.exit(1)

    sample_file = sys.argv[1]
    try:
        with open(sample_file, "r") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        sys.exit(1)
    
    # Generate schema for the block table using all keys except 'tx'
    block_schema = generate_table_schema("block_autogen", data, skip_keys=["tx"])
    print("-- Auto-generated schema for block table:")
    print(block_schema)
    print("\n")

    # If the sample block has a 'tx' field and it's a non-empty list, generate a schema for transactions.
    if "tx" in data and isinstance(data["tx"], list) and len(data["tx"]) > 0:
        tx_sample = data["tx"][0]  # use the first transaction as a sample
        tx_schema = generate_table_schema("transaction_autogen", tx_sample)
        print("-- Auto-generated schema for transaction table:")
        print(tx_schema)

if __name__ == "__main__":
    main()
