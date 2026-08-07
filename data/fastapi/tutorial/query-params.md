# Query Parameters

When you declare other function parameters that are not part of the path parameters, they are automatically interpreted as "query" parameters.

```python
from fastapi import FastAPI

app = FastAPI()

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


@app.get("/items/")
def read_item(skip: int = 0, limit: int = 10):
    return fake_items_db[skip : skip + limit]
```

The query is the set of key-value pairs that go after the `?` in a URL, separated by `&` characters.

For example, in the URL:

```text
http://127.0.0.1:8000/items/?skip=0&limit=10
```

...the query parameters are:

- `skip`: with a value of `0`
- `limit`: with a value of `10`

### Defaults and Optional Parameters

Because they have default values, `skip` and `limit` are optional. If you go to `http://127.0.0.1:8000/items/`, it defaults to `skip=0` and `limit=10`.

To declare an optional query parameter without a default value, use Python typing:

```python
from typing import Optional
from fastapi import FastAPI

app = FastAPI()


@app.get("/items/{item_id}")
def read_item(item_id: str, q: Optional[str] = None):
    if q:
        return {"item_id": item_id, "q": q}
    return {"item_id": item_id}
```
