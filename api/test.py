from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Test OK"}

@app.get("/health")
async def health():
    return {"status": "OK"}

handler = app 