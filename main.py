import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello World"}


if __name__ == '__main__':
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
