# Path Parameters

You can declare path "parameters" or "variables" with the same syntax used by Python format strings.

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}
```

The value of the path parameter `item_id` will be passed to your function as the argument `item_id`.

### Data conversion and validation

If you declare the type as `int`:

```python
@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}
```

FastAPI will automatically convert the string from the URL path into a Python `int`.

If the value is not a valid integer, for example if someone visits `/items/foo`, FastAPI returns an HTTP 422 Unprocessable Entity error with a clear JSON describing the validation error.

### Path parameters containing paths

Using an option directly from Starlette you can declare a path parameter containing a path using a URL like:

```python
@app.get("/files/{file_path:path}")
def read_file(file_path: str):
    return {"file_path": file_path}
```

In this case, the name of the parameter is `file_path`, and the last part, `:path`, tells it that the parameter should match any path.
