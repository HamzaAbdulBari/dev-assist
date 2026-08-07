# First Steps

The simplest FastAPI file could look like this:

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}
```

### Run the code

Run the live server with:

```bash
uvicorn main:app --reload
```

The command `uvicorn main:app` refers to:
- `main`: the file `main.py` (the Python "module").
- `app`: the object created inside `main.py` with the line `app = FastAPI()`.
- `--reload`: make the server restart after code changes. Only use this for local development.

### Interactive API docs

Go to `http://127.0.0.1:8000/docs`. You will see the automatic interactive API documentation provided by Swagger UI.

### Alternative API docs

Go to `http://127.0.0.1:8000/redoc`. You will see the alternative documentation provided by ReDoc.

### Recap

- Import `FastAPI`.
- Create an `app` instance.
- Write a path operation decorator like `@app.get("/")`.
- Write a path operation function like `def read_root():`.
- Return content (a dictionary, list, string, number, or Pydantic model).
