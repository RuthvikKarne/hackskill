from fastapi import FastAPI

app = FastAPI(title="Smart Health API")

@app.get("/")
def read_root():
    return {"message": "Welcome to Smart Health API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
