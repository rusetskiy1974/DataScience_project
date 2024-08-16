import uvicorn
from fastapi import FastAPI

from app.routers.all import all_routers

app = FastAPI()


for router in all_routers:
    app.include_router(router)


if __name__ == "__main__":
    uvicorn.run(app="main:app", reload=True)
