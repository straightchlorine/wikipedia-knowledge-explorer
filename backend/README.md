# Backend Component of the Application

Backend is based on FastAPI and Wikipedia API to retrieve articles.

---

### Deployment

You can deploy the backend either locally using `uvicorn` or as a container using Docker.

---
#### Deploy locally

Following command will start the FastAPI server on the localhost on a default port `8000`:

```bash
$ uvicorn wiki.main:wiki_exp
```

You can adjust it to run on a different port, host or just enable `--reload` flag for development. You can see available options in the [uvicorn documentation](https://www.uvicorn.org/settings/).

---
#### Deploy in a container

Otherwise, you can build and run the Docker container:

```bash
$ docker build -t wiki-backend .
$ docker run -p 8000:8000 wiki-backend
```

---
### Testing

For the testing `pytest` is used, so to run all of the backend tests:

```bash
$ pytest -v tests
```
---
### Example usage:

```bash
$ curl "http://localhost:8000/articles/?query=Python" | jq
{
    "query": "Python",
    "articles": [
    "Python (programming language)",
    "Python",
    "Monty Python",
    "Python (codename)",
    "Reticulated python"
    ]
}
```
