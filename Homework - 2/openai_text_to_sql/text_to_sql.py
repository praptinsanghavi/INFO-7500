import os
import logging
import openai
from openai import OpenAI

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Ensure API key is set properly
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logging.error("❌ OPENAI_API_KEY is not set. Please set it before running the script.")
    logging.info("➡ To set the API key in PowerShell, use: $env:OPENAI_API_KEY='your-api-key-here'")
    logging.info("➡ To set it in CMD, use: set OPENAI_API_KEY=your-api-key-here")
    logging.info("➡ To set it in Bash, use: export OPENAI_API_KEY='your-api-key-here'")
    exit(1)

# Initialize OpenAI client
try:
    client = OpenAI()
except Exception as e:
    logging.error(f"❌ Failed to initialize OpenAI client: {e}")
    exit(1)

# Define SQL schema
sql_schema = """
CREATE TABLE Employees (
    EmployeeID INT PRIMARY KEY,
    FirstName VARCHAR(50),
    LastName VARCHAR(50),
    Department VARCHAR(50),
    Salary DECIMAL(10, 2),
    HireDate DATE
);

CREATE TABLE Departments (
    DepartmentID INT PRIMARY KEY,
    DepartmentName VARCHAR(50),
    Location VARCHAR(100)
);

CREATE TABLE Salaries (
    SalaryID INT PRIMARY KEY,
    EmployeeID INT,
    SalaryAmount DECIMAL(10, 2),
    EffectiveDate DATE,
    FOREIGN KEY (EmployeeID) REFERENCES Employees(EmployeeID)
);
"""

# Take user input for question
question = input("🔍 Enter your natural language query: ").strip()

# Validate input
if not question:
    logging.error("❌ No input provided. Please enter a valid question.")
    exit(1)

# Prepare prompt for OpenAI
prompt = f"""
You are an SQL expert. Based on the following SQL schema, generate an SQL query to answer the question below.

SQL Schema:
{sql_schema}

Question:
{question}

Only provide the SQL query, no explanations.
"""

# API parameters
model = "gpt-4o"
max_tokens = 150
temperature = 0.3  # Lower temperature for deterministic SQL
top_p = 0.9

try:
    # Call OpenAI API
    logging.info("⏳ Sending request to OpenAI...")
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are an SQL expert."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p
    )

    # Extract the SQL query response
    if response.choices:
        generated_sql = response.choices[0].message.content.strip()
        print("\n✅ **Generated SQL Query:**\n")
        print(generated_sql)
    else:
        logging.error("❌ No valid response received from OpenAI.")
        exit(1)

except openai.OpenAIError as api_error:
    logging.error(f"🚨 OpenAI API error: {api_error}")
    exit(1)
except Exception as e:
    logging.error(f"🚨 An unexpected error occurred: {e}")
    exit(1)
