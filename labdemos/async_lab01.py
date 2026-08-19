import asyncio
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file
client = OpenAI()


async def call_llm(prompt):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


async def main():
    results = await asyncio.gather(
        call_llm("Tell me a simple story."), 
        call_llm("What is the morale of the story."), 
        call_llm("Who is the protaganist and antagonist.")
    )
    print("Results from LLM calls:")
    for i, res in enumerate(results, start=1):
        print(f"Result {i}: {res}")


if __name__ == "__main__":
    asyncio.run(main())
    