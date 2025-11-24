# Minimal admin models module to satisfy alembic env imports.
# Alembic's env.py only needs `Base.metadata` to exist. The real models
# are defined in migration scripts; this file provides a declarative Base.
from app.db.base_class import Base

__all__ = ["Base"]
