from agents import Agent, Runner, function_tool
import sqlite3
from dotenv import load_dotenv

load_dotenv(override=True)

@function_tool
def run_sql(query: str) -> str:
    
    conn = sqlite3.connect(r"D:\git\AgenticAI\agenticai\14_advanced\03_llm_examples\sales.db")
    cursor = conn.cursor()

    cursor.execute(query)    
    
    rows = cursor.fetchall()

    conn.close()

    return str(rows)

agent = Agent(
    name="Sales Assistant",
    model="gpt-4o-mini",
    instructions="""
    You help users answer questions about the sales database.
    Use the run_sql tool whenever database information is needed.
    """,
    tools=[run_sql],
)

# Run agent in loop with sample quesiton from user input
#run in loop until exit is given as input

while True:
    user_input = input("Enter your question (or 'exit' to quit): ")
    if user_input.lower() == "exit":
        break

    result = Runner.run_sync(
        agent,
        input=user_input
    )

    print(result.final_output)