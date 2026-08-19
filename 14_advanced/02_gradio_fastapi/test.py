from fastapi import FastAPI

# 1. Initialize the FastAPI app
app = FastAPI()

# 2. Add the missing root route handler
@app.get("/")
async def home():
    return {"message": "Welcome to my FastAPI backend!"}