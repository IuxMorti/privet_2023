from fastapi import FastAPI,APIRouter
from starlette.middleware.cors import CORSMiddleware

from api.auth.routers import auth_api
from api.user.routers import user_api
from api.arrival.routers import arrival_api
from api.tasks.routers import task_api

app = FastAPI()


origins = [
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT", "HEAD"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers", "Access-Control-Allow-Origin",
                   "Authorization", "filename", "types"],
)

api_v1 = APIRouter(prefix="/api/v1", tags=["v1"])
api_v1.include_router(auth_api)
api_v1.include_router(user_api)
api_v1.include_router(arrival_api)
api_v1.include_router(task_api)


app.include_router(api_v1, prefix="")

if __name__ == '__main__':
    import uvicorn

    uvicorn.run('main:app', port=6370, reload=True)
