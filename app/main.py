from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app import exceptions
from app.routers.categories import router as category_router
from app.routers.products import router as product_router
from app.routers.users import router as user_router
from app.routers.reviews import router as review_router


app = FastAPI()


app.include_router(category_router)
app.include_router(product_router)
app.include_router(user_router)
app.include_router(review_router)


@app.exception_handler(exceptions.NotFoundError)
async def not_found_handler(_: Request, exc: exceptions.NotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )


@app.exception_handler(exceptions.BadRequestError)
async def bad_request_handler(_: Request, exc: exceptions.BadRequestError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )


@app.exception_handler(exceptions.ForbiddenError)
async def forbidden_handler(_: Request, exc: exceptions.ForbiddenError):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": str(exc)},
    )
