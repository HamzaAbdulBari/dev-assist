# Request Body

When you need to send data from a client (let's say, a browser) to your API, you send it as a **request body**.

A **request body** is data sent by the client to your API. A **response body** is the data your API sends to the client.

To declare a request body, you use Pydantic models with all their power and benefits.

### Import Pydantic's BaseModel

First, you need to import `BaseModel` from `pydantic`:

```python
from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel


class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None


app = FastAPI()


@app.post("/items/")
def create_item(item: Item):
    return item
```

### Declare it as a parameter

To add it to your path operation, declare it the same way you declared path and query parameters, and give it the type of the model you created (`Item`).

### Results

With just that Python type declaration, FastAPI will:

- Read the body of the request as JSON.
- Convert the corresponding types (if needed).
- Validate the data. If the data is invalid, it will return a nice and clear error indicating exactly where and what was the incorrect data.
- Give you the received data in the parameter `item`. As you declared it in the function to be of type `Item`, you will also have all the editor support (completion, etc) for all of the attributes and their types.
- Generate JSON Schema definitions for your models that can also be used anywhere else relevant for your project.
- Those schemas will be part of the generated OpenAPI schema, and used by the automatic documentation UIs.
