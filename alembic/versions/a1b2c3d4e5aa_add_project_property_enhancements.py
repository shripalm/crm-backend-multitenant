"""Add enhanced fields to projects and properties tables

Revision ID: a1b2c3d4e5aa
Revises: a1b2c3d4e5a9
Create Date: 2025-12-17 10:10:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5aa'
down_revision = 'a1b2c3d4e5a9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check and drop existing enum types first (to handle case mismatches)
    op.execute("DROP TYPE IF EXISTS projecttype CASCADE")
    op.execute("DROP TYPE IF EXISTS constructionstatus CASCADE")
    op.execute("DROP TYPE IF EXISTS facing CASCADE")
    op.execute("DROP TYPE IF EXISTS furnishedstatus CASCADE")
    
    # Create custom enum types for PostgreSQL with lowercase values
    op.execute("CREATE TYPE projecttype AS ENUM ('residential', 'commercial', 'retail', 'mixed_use', 'land')")
    op.execute("CREATE TYPE constructionstatus AS ENUM ('under_construction', 'ready_to_move')")
    op.execute("CREATE TYPE facing AS ENUM ('north', 'south', 'east', 'west')")
    op.execute("CREATE TYPE furnishedstatus AS ENUM ('furnished', 'unfurnished', 'semifurnished')")
    
    # Add new columns to projects table
    op.add_column('projects', sa.Column('project_type', sa.Enum('residential', 'commercial', 'retail', 'mixed_use', 'land', name='projecttype'), nullable=True))
    op.add_column('projects', sa.Column('address', sa.Text(), nullable=True))
    op.add_column('projects', sa.Column('photo', sa.Text(), nullable=True))
    op.add_column('projects', sa.Column('brochure', sa.Text(), nullable=True))
    op.add_column('projects', sa.Column('possession_date', sa.Date(), nullable=True))
    op.add_column('projects', sa.Column('construction_status', sa.Enum('under_construction', 'ready_to_move', name='constructionstatus'), nullable=True))
    op.add_column('projects', sa.Column('highlights', sa.Text(), nullable=True))
    op.add_column('projects', sa.Column('total_towers', sa.Numeric(precision=10, scale=2), nullable=True))
    op.add_column('projects', sa.Column('no_of_floors', sa.Numeric(precision=10, scale=2), nullable=True))
    op.add_column('projects', sa.Column('no_of_units', sa.Numeric(precision=10, scale=2), nullable=True))
    op.add_column('projects', sa.Column('flats_per_floor', sa.Numeric(precision=10, scale=2), nullable=True))
    op.add_column('projects', sa.Column('lifts_per_floor', sa.Numeric(precision=10, scale=2), nullable=True))
    op.add_column('projects', sa.Column('parking_types', sa.Text(), nullable=True))
    op.add_column('projects', sa.Column('starting_amount', sa.Numeric(precision=15, scale=2), nullable=True))
    op.add_column('projects', sa.Column('rera_number', sa.String(length=100), nullable=True))
    op.add_column('projects', sa.Column('gst_number', sa.String(length=50), nullable=True))
    op.add_column('projects', sa.Column('consultant', sa.String(length=255), nullable=True))
    op.add_column('projects', sa.Column('architect', sa.String(length=255), nullable=True))
    op.add_column('projects', sa.Column('url_title', sa.String(length=500), nullable=True))
    op.add_column('projects', sa.Column('url_description', sa.String(length=1000), nullable=True))
    op.add_column('projects', sa.Column('description', sa.Text(), nullable=True))
    
    # Add new columns to properties table
    op.add_column('properties', sa.Column('no_of_bedrooms', sa.Numeric(precision=5, scale=0), nullable=True))
    op.add_column('properties', sa.Column('amenities', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('properties', sa.Column('rate_per_sqft', sa.Numeric(precision=15, scale=2), nullable=True))
    op.add_column('properties', sa.Column('owner_name', sa.Text(), nullable=True))
    op.add_column('properties', sa.Column('building_name', sa.Text(), nullable=True))
    op.add_column('properties', sa.Column('listing_date', sa.Date(), nullable=True))
    op.add_column('properties', sa.Column('facing', sa.Enum('north', 'south', 'east', 'west', name='facing'), nullable=True))
    op.add_column('properties', sa.Column('furnished_status', sa.Enum('furnished', 'unfurnished', 'semifurnished', name='furnishedstatus'), nullable=True))
    op.add_column('properties', sa.Column('age_of_property', sa.Numeric(precision=5, scale=0), nullable=True))
    op.add_column('properties', sa.Column('address', sa.Text(), nullable=True))
    op.add_column('properties', sa.Column('image', sa.Text(), nullable=True))
    op.add_column('properties', sa.Column('description', sa.Text(), nullable=True))


def downgrade() -> None:
    # Remove columns from properties table
    op.drop_column('properties', 'description')
    op.drop_column('properties', 'image')
    op.drop_column('properties', 'address')
    op.drop_column('properties', 'age_of_property')
    op.drop_column('properties', 'furnished_status')
    op.drop_column('properties', 'facing')
    op.drop_column('properties', 'listing_date')
    op.drop_column('properties', 'building_name')
    op.drop_column('properties', 'owner_name')
    op.drop_column('properties', 'rate_per_sqft')
    op.drop_column('properties', 'amenities')
    op.drop_column('properties', 'no_of_bedrooms')
    
    # Remove columns from projects table
    op.drop_column('projects', 'description')
    op.drop_column('projects', 'url_description')
    op.drop_column('projects', 'url_title')
    op.drop_column('projects', 'architect')
    op.drop_column('projects', 'consultant')
    op.drop_column('projects', 'gst_number')
    op.drop_column('projects', 'rera_number')
    op.drop_column('projects', 'starting_amount')
    op.drop_column('projects', 'parking_types')
    op.drop_column('projects', 'lifts_per_floor')
    op.drop_column('projects', 'flats_per_floor')
    op.drop_column('projects', 'no_of_units')
    op.drop_column('projects', 'no_of_floors')
    op.drop_column('projects', 'total_towers')
    op.drop_column('projects', 'highlights')
    op.drop_column('projects', 'construction_status')
    op.drop_column('projects', 'possession_date')
    op.drop_column('projects', 'brochure')
    op.drop_column('projects', 'photo')
    op.drop_column('projects', 'address')
    op.drop_column('projects', 'project_type')
    
    # Drop custom enum types
    op.execute("DROP TYPE IF EXISTS furnishedstatus")
    op.execute("DROP TYPE IF EXISTS facing")
    op.execute("DROP TYPE IF EXISTS constructionstatus")
    op.execute("DROP TYPE IF EXISTS projecttype")
