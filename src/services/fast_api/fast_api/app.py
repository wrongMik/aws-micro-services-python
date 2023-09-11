import os
from uuid import uuid4

import uvicorn
from mangum import Mangum
from fastapi import FastAPI, HTTPException, status

from micro_core.logging_config import configure_logging

from fast_api.routers import users_router
from fast_api.models.message_model import Message, MessageWithUUID
from fast_api.handlers.exception_handler import exception_handler
from fast_api.middlewares.logging_middleware import LoggingMiddleware
from fast_api.handlers.http_exception_handler import http_exception_handler
from fast_api.middlewares.correlation_id_middleware import CorrelationIdMiddleware

app = FastAPI(
    title="fast-api",
    description="Fast API - Service",
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal Server Error", "model": MessageWithUUID},
        status.HTTP_400_BAD_REQUEST: {"description": "Bad request syntax or unsupported method", "model": Message},
        status.HTTP_404_NOT_FOUND: {"description": "Not Found", "model": Message},
    },
)

###############################################################################
#   Logging configuration                                                     #
###############################################################################

configure_logging(
    service="fast-api",
    instance=str(uuid4()),
    level=os.getenv("LOG_LEVEL", "DEBUG"),
)

###############################################################################
#   Error handlers configuration                                              #
###############################################################################

app.add_exception_handler(Exception, exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)

###############################################################################
#   Middlewares configuration                                                 #
###############################################################################

# Tip : middleware order : CorrelationIdMiddleware > LoggingMiddleware -> reverse order
app.add_middleware(LoggingMiddleware)
app.add_middleware(CorrelationIdMiddleware)

###############################################################################
#   Routers configuration                                                     #
###############################################################################


@app.get("/users/health", include_in_schema=False)
def health():
    return Message(message="healthy")


app.include_router(users_router.router)

###############################################################################
#   Handler for AWS Lambda                                                    #
###############################################################################

handler = Mangum(app)

###############################################################################
#   Run the self contained application                                        #
###############################################################################

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
