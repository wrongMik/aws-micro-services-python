from typing import Union

import uvicorn
from mangum import Mangum
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()
handler = Mangum(app)

# trying to differentiate the urls for the docs when we will plug the
# dirrent api in the same API Gateway
app = FastAPI(openapi_url="/v1/simpler/openapi.json", docs_url="/v1/simpler/docs")


@app.get("/")
def read_root():
    return {"Welcome to": "My first FastAPI depolyment"}


@app.get("/{text}")
def read_text(text: str):
    return JSONResponse({"result": text})


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return JSONResponse({"item_id": item_id, "q": q})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=6000)
