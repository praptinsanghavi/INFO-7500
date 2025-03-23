import os
import logging
import openai
import sqlite3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Ensure API key is set properly
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logging.error("❌ OPENAI_API_KEY is not set. Please set it before running the script.")
    exit(1)

# Function to load the prompt template
def load_prompt_template():
    """Reads the prompt template from the prompt.txt file."""
    try:
        with open("prompt.txt", "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        logging.error("❌ prompt.txt file not found! Make sure it exists in the same directory as the script.")
        exit(1)

def generate_sql_query(natural_language_question):
    """Generates an SQL query from a natural language question using OpenAI API."""
    prompt_template = load_prompt_template()
    prompt = prompt_template.replace("{question_placeholder}", natural_language_question)

    try:
        logging.info("⏳ Sending request to OpenAI...")

        # ✅ Corrected OpenAI API usage
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an SQL expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=200,
            top_p=0.9
        )

        # ✅ Extract SQL query from response
        generated_sql = response.choices[0].message.content.strip()
        logging.info("✅ SQL query generated successfully.")
        return generated_sql

    except openai.OpenAIError as api_error:
        logging.error(f"🚨 OpenAI API error: {api_error}")
    except Exception as e:
        logging.error(f"🚨 An unexpected error occurred: {e}")
    
    return None

def execute_sql_query(query):
    """Executes the generated SQL query in a test SQLite database."""
    try:
        conn = sqlite3.connect(":memory:")  # In-memory database for testing
        cursor = conn.cursor()

        # Create tables
        cursor.executescript("""
        CREATE TABLE Employees (
            EmployeeID INT PRIMARY KEY,
            FirstName TEXT,
            LastName TEXT,
            Department TEXT,
            Salary DECIMAL(10, 2),
            HireDate DATE
        );

        CREATE TABLE Departments (
            DepartmentID INT PRIMARY KEY,
            DepartmentName TEXT,
            Location TEXT
        );

        CREATE TABLE Salaries (
            SalaryID INT PRIMARY KEY,
            EmployeeID INT,
            SalaryAmount DECIMAL(10, 2),
            EffectiveDate DATE,
            FOREIGN KEY (EmployeeID) REFERENCES Employees(EmployeeID)
        );

        -- Sample Data
        INSERT INTO Employees VALUES (1, 'Alice', 'Smith', 'HR', 75000.00, '2022-01-15');
        INSERT INTO Employees VALUES (2, 'Bob', 'Johnson', 'Engineering', 85000.00, '2021-03-10');
        INSERT INTO Departments VALUES (1, 'HR', 'New York'), (2, 'Engineering', 'San Francisco');
        INSERT INTO Salaries VALUES (1, 1, 75000.00, '2022-01-15'), (2, 2, 85000.00, '2021-03-10');
        """)

        cursor.execute(query)
        results = cursor.fetchall()

        print("\n📊 Query Results:")
        for row in results:
            print(row)

        conn.close()
    except sqlite3.Error as db_error:
        logging.error(f"❌ Database error: {db_error}")

if __name__ == "__main__":
    # Get user input
    question = input("🔍 Enter your natural language question: ").strip()

    if not question:
        logging.error("❌ No input provided. Please enter a valid question.")
        exit(1)

    # Generate SQL Query
    sql_query = generate_sql_query(question)
    
    if sql_query:
        print("\n✅ **Generated SQL Query:**")
        print(sql_query)

        # Execute the SQL Query
        execute_sql_query(sql_query)
