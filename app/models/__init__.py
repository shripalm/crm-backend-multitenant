from .admin import Base  # keep existing minimal admin export
from .projects import Project, Property

__all__ = ["Base", "Project", "Property"]
