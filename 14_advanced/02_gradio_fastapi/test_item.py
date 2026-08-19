from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Initialize the FastAPI application
app = FastAPI(title="Item Management API")

# Define a Pydantic model for request data validation
class Item(BaseModel):
    name: str
    price: float
    description: str | None = None
    on_sale: bool = False

# Temporary in-memory database simulation
database = {}

# 1. GET Route: Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI example!"}

# 2. GET Route: Path and Query parameters
@app.get("/items/{item_id}")
def read_item(item_id: int, details: bool = False):
    if item_id not in database:
        raise HTTPException(status_code=404, detail="Item not found")
    
    item = database[item_id]
    if details:
        return {"item_id": item_id, "data": item}
    return {"item_id": item_id, "name": item.name}

# 3. POST Route: Creating data with request body validation
@app.post("/items/{item_id}")
def create_item(item_id: int, item: Item):
    if item_id in database:
        raise HTTPException(status_code=400, detail="Item ID already exists")
    
    database[item_id] = item
    return {"message": "Item created successfully", "item": item}

@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    if item_id not in database:
        raise HTTPException(status_code=404, detail="Item not found")
    
    del database[item_id]
    return {"message": "Item deleted successfully"}