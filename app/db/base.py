from .base_class import Base

# Compatibility module: alembic expects `app.db.base.Base`
# This file re-exports Base from base_class.py
__all__ = ["Base"]
