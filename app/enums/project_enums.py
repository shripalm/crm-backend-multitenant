"""
Shared enums for Project model and schemas
"""
from enum import Enum


class ProjectType(str, Enum):
    residential = "residential"
    commercial = "commercial"
    retail = "retail"
    mixed_use = "mixed_use"
    land = "land"


class ConstructionStatus(str, Enum):
    under_construction = "under_construction"
    ready_to_move = "ready_to_move"


class Facing(str, Enum):
    north = "north"
    south = "south"
    east = "east"
    west = "west"


class FurnishedStatus(str, Enum):
    furnished = "furnished"
    unfurnished = "unfurnished"
    semifurnished = "semifurnished"
