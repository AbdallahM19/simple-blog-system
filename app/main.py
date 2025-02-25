"""/app/main.py"""

import uvicorn

from contextlib import asynccontextmanager

from fastapi import FastAPI
from database import create_db_and_tables, delete_db
from routes import *


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield
    # delete_db()


app = FastAPI(lifespan=lifespan)

app.include_router(blog_routes)
app.include_router(user_routes)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)