## FastAPI + Mangum

The service that take care of the web application used to retrieve information about the users.

The service is a web application build using Python FastAPI framework,
it can be run inside a local container or inside an AWS Lambda container as well.

## Run locally

You can either use the following command :

```bash
cd src/fast_api
python -m fast_api.app
```

Or deploy on uvicorn :

```bash
cd src/fast_api
uvicorn fast_api.app:app --reload --host 0.0.0.0 --port 5000
```

You can test the application by using the following command :

```bash
curl http://localhost:5000/users/
```

Or open a browser at http://localhost:5000/docs to see the application running

## Build the 'regular' container

This command builds a container which will run a Uvicorn server and deploy the ASGI app on it :

```bash
docker build -t fast-api . -f ./docker/Dockerfile.fast-api
```

## Run the container

The command starts the container :

```bash
docker run -p 5000:5000 fast-api:latest
```

You can make a test with this command :

```bash
curl http://localhost:5000/users/
```
