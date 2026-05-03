from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Healthcare Inventory Management System Backend"}

@app.get("/health")
async def health():
    return {"status": "healthy"}