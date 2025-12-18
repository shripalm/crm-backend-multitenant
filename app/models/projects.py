from sqlalchemy import Column, Text, Date, Numeric, TIMESTAMP, ForeignKey, Boolean, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import sqlalchemy as sa

from app.db.base_class import Base
from app.enums.project_enums import ProjectType, ConstructionStatus, Facing, FurnishedStatus


class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()"))
    name = Column(Text, nullable=False)
    developer = Column(Text, nullable=True)
    location = Column(Text, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    meta = Column(JSONB, nullable=True)
    
    # New fields
    project_type = Column(Enum(ProjectType), nullable=True)
    address = Column(Text, nullable=True)
    photo = Column(Text, nullable=True)  # URL or path to uploaded photo
    brochure = Column(Text, nullable=True)  # URL or path to uploaded brochure
    possession_date = Column(Date, nullable=True)
    construction_status = Column(Enum(ConstructionStatus), nullable=True)
    highlights = Column(Text, nullable=True)
    total_towers = Column(Numeric, nullable=True)
    no_of_floors = Column(Numeric, nullable=True)
    no_of_units = Column(Numeric, nullable=True)
    flats_per_floor = Column(Numeric, nullable=True)
    lifts_per_floor = Column(Numeric, nullable=True)
    parking_types = Column(Text, nullable=True)
    starting_amount = Column(Numeric, nullable=True)
    rera_number = Column(Text, nullable=True)
    gst_number = Column(Text, nullable=True)
    consultant = Column(Text, nullable=True)
    architect = Column(Text, nullable=True)
    url_title = Column(Text, nullable=True)
    url_description = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()"))
    is_deleted = Column(Boolean, default=False)

    # relationship to properties
    properties = relationship("Property", back_populates="project", cascade="all, delete-orphan")


class Property(Base):
    __tablename__ = "properties"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()"))
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=True)
    unit_number = Column(Text, nullable=True)
    size = Column(Numeric, nullable=True)
    price = Column(Numeric, nullable=True)
    status = Column(Text, nullable=True)
    attributes = Column(JSONB, nullable=True)
    
    # New fields for Property
    no_of_bedrooms = Column(Numeric, nullable=True)
    amenities = Column(JSONB, nullable=True)  # For parking, gym, swimming pool, etc.
    rate_per_sqft = Column(Numeric, nullable=True)
    owner_name = Column(Text, nullable=True)
    building_name = Column(Text, nullable=True)
    listing_date = Column(Date, nullable=True)
    facing = Column(Enum(Facing), nullable=True)
    furnished_status = Column(Enum(FurnishedStatus), nullable=True)
    age_of_property = Column(Numeric, nullable=True)
    address = Column(Text, nullable=True)
    image = Column(Text, nullable=True)  # URL or path to uploaded image
    description = Column(Text, nullable=True)
    
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()"))
    is_deleted = Column(Boolean, default=False)

    project = relationship("Project", back_populates="properties")













