# Dependencies

FastAPI has a very powerful but intuitive **Dependency Injection** system.

It is designed to be very simple to use, and to make it very easy for any developer to integrate other components with FastAPI.

### What is "Dependency Injection"

"Dependency Injection" means, in programming, that there is a way for your code (in this case, your path operation functions) to declare things that it requires to work and use: "dependencies".

And then, that system (in this case FastAPI) will take care of doing whatever is needed to provide your code with those dependencies ("inject" the dependencies).

This is very useful when you need to:
- Have shared logic (the same code logic over and over again).
- Share database connections.
- Enforce security, authentication, role requirements, etc.
- And many other things...

### First Steps

Let's see a very simple example:

```python
from typing import Optional
from fastapi import Depends, FastAPI

app = FastAPI()


async def common_parameters(q: Optional[str] = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}


@app.get("/items/")
async def read_items(commons: dict = Depends(common_parameters)):
    return commons
```

### Share `Annotated` dependencies

In modern FastAPI, you can use `Annotated` from `typing` (or `typing_extensions` in older Python versions):

```python
from typing import Annotated
from fastapi import Depends, FastAPI

app = FastAPI()


async def common_parameters(q: str | None = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}

CommonsDep = Annotated[dict, Depends(common_parameters)]


@app.get("/items/")
async def read_items(commons: CommonsDep):
    return commons
```
