# Settings and Environment Variables

In many situations your application might need some external settings or configurations, for example secret keys, database credentials, credentials for email services, etc.

Most of these settings are variable (can change), like database URLs. And many could be sensitive, like secrets.

For this, the common approach is to provide them in environment variables.

### Pydantic Settings

You can use `pydantic-settings` to handle settings and environment variables:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "FastAPI Documentation Assistant"
    admin_email: str
    items_per_user: int = 50

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
```

### Reading `.env` files

If you have many different settings that possibly change in different environments (like development, testing, production), you can use a `.env` file to configure them.

FastAPI integrates smoothly with Pydantic settings to load and validate variables at runtime.
