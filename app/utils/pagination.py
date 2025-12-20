
from typing import Any, Dict, Generic, List, Optional, Sequence, TypeVar, Union
from pydantic import BaseModel, Field, field_validator, ConfigDict
from enum import Enum
from sqlalchemy import Select, asc, desc, func, text, select
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession
from math import ceil

# T = TypeVar('T', bound=DeclarativeBase)

T = TypeVar('T')              # for API / response
ORM = TypeVar('ORM', bound=DeclarativeBase)  # for SQLAlchemy only


class SortDirection(str, Enum):
    ASC = "asc"
    DESC = "desc"

class PaginationParams(BaseModel):
    """Pagination parameters with validation"""
    page: int = Field(1, ge=1, description="Page number (starts from 1)")
    size: int = Field(20, ge=1, le=100, description="Items per page (max 100)")
    sort_by: Optional[str] = Field(None, description="Field to sort by")
    sort_direction: SortDirection = Field(SortDirection.DESC, description="Sort direction")
    
    @field_validator('sort_by')
    @classmethod
    def validate_sort_field(cls, v):
        if v is not None:
            v = v.strip()
            if not v:
                return None
            # Prevent SQL injection by allowing only alphanumeric and underscore
            if not v.replace('_', '').isalnum():
                raise ValueError("Invalid sort field name")
        return v

class PaginationMeta(BaseModel, Generic[T]):
    """Pagination metadata"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    current_page: int
    total_pages: int
    total_items: int
    items_per_page: int
    has_next: bool
    has_previous: bool
    next_page: Optional[int] = None
    previous_page: Optional[int] = None

class PaginatedResponse(BaseModel, Generic[T]):
    """Standard paginated response structure"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    data: List[T]
    meta: PaginationMeta
    message: str = "Data retrieved successfully"

class FilterParams(BaseModel):
    """Base filter parameters"""
    search: Optional[str] = Field(None, min_length=1, max_length=100, description="Search term")
    
    def get_search_conditions(self, model_class):
        """Get search conditions for the model"""
        if not self.search:
            return []
        
        search_term = f"%{self.search}%"
        conditions = []
        
        # Add search conditions for common string fields
        string_fields = [
            field.name for field in model_class.__table__.columns 
            if field.type.python_type in (str, )
        ]
        
        for field in string_fields:
            conditions.append(getattr(model_class, field).ilike(search_term))
        
        return conditions

class ContactFilterParams(FilterParams):
    """Specific filters for contact model"""
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    source: Optional[str] = Field(None, max_length=100)
    project_name: Optional[str] = Field(None, max_length=255)
    property_type: Optional[str] = Field(None, max_length=100)
    budget_range: Optional[str] = Field(None, max_length=100)
    has_email: Optional[bool] = Field(None, description="Filter contacts with/without email")
    has_phone: Optional[bool] = Field(None, description="Filter contacts with/without phone")

class Paginator:
    """Industrial-grade paginator with filtering and sorting"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def paginate(
        self,
        query: Select,
        pagination_params: PaginationParams,
        filter_params: Optional[FilterParams] = None,
        model_class: Optional[T] = None
    ) -> PaginatedResponse[Any]:
        """
        Paginate a query with optional filtering and sorting
        
        Args:
            query: SQLAlchemy Select query
            pagination_params: Pagination parameters
            filter_params: Optional filter parameters
            model_class: Model class for filtering (required if using filters)
        
        Returns:
            PaginatedResponse with data and metadata
        """
        # Apply filters
        if filter_params and model_class:
            query = self._apply_filters(query, filter_params, model_class)
        
        # Apply sorting
        query = self._apply_sorting(query, pagination_params, model_class)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_count = await self.session.scalar(count_query)
        
        # Calculate pagination
        offset = (pagination_params.page - 1) * pagination_params.size
        total_pages = ceil(total_count / pagination_params.size) if total_count > 0 else 1
        
        # Apply pagination
        query = query.offset(offset).limit(pagination_params.size)
        
        # Execute query
        result = await self.session.execute(query)
        items = result.scalars().all()
        
        # Build metadata
        meta = PaginationMeta(
            current_page=pagination_params.page,
            total_pages=total_pages,
            total_items=total_count,
            items_per_page=pagination_params.size,
            has_next=pagination_params.page < total_pages,
            has_previous=pagination_params.page > 1,
            next_page=pagination_params.page + 1 if pagination_params.page < total_pages else None,
            previous_page=pagination_params.page - 1 if pagination_params.page > 1 else None
        )
        
        return PaginatedResponse(
            data=list(items),
            meta=meta
        )
    
    def _apply_filters(self, query: Select, filter_params: FilterParams, model_class: T) -> Select:
        """Apply filters to the query"""
        conditions = []
        
        # Apply search filters
        search_conditions = filter_params.get_search_conditions(model_class)
        if search_conditions:
            from sqlalchemy import or_
            conditions.append(or_(*search_conditions))
        
        # Apply specific filters for ContactFilterParams
        if isinstance(filter_params, ContactFilterParams):
            if filter_params.city:
                conditions.append(model_class.city.ilike(f"%{filter_params.city}%"))
            if filter_params.state:
                conditions.append(model_class.state.ilike(f"%{filter_params.state}%"))
            if filter_params.source:
                conditions.append(model_class.source.ilike(f"%{filter_params.source}%"))
            if filter_params.project_name:
                conditions.append(model_class.project_name.ilike(f"%{filter_params.project_name}%"))
            if filter_params.property_type:
                conditions.append(model_class.property_type.ilike(f"%{filter_params.property_type}%"))
            if filter_params.budget_range:
                conditions.append(model_class.budget_range.ilike(f"%{filter_params.budget_range}%"))
            if filter_params.has_email is not None:
                if filter_params.has_email:
                    conditions.append(model_class.email.isnot(None))
                else:
                    conditions.append(model_class.email.is_(None))
            if filter_params.has_phone is not None:
                if filter_params.has_phone:
                    conditions.append(model_class.contact_no.isnot(None))
                else:
                    conditions.append(model_class.contact_no.is_(None))
        
        if conditions:
            from sqlalchemy import and_
            query = query.where(and_(*conditions))
        
        return query
    
    def _apply_sorting(
        self, 
        query: Select, 
        pagination_params: PaginationParams, 
        model_class: Optional[T] = None
    ) -> Select:
        """Apply sorting to the query"""
        if pagination_params.sort_by and model_class:
            # Validate that the sort field exists
            if hasattr(model_class, pagination_params.sort_by):
                sort_field = getattr(model_class, pagination_params.sort_by)
                if pagination_params.sort_direction == SortDirection.ASC:
                    query = query.order_by(asc(sort_field))
                else:
                    query = query.order_by(desc(sort_field))
            else:
                # Fallback to created_at if invalid field
                if hasattr(model_class, 'created_at'):
                    if pagination_params.sort_direction == SortDirection.ASC:
                        query = query.order_by(asc(model_class.created_at))
                    else:
                        query = query.order_by(desc(model_class.created_at))
        else:
            # Default sorting by created_at desc
            if model_class and hasattr(model_class, 'created_at'):
                query = query.order_by(desc(model_class.created_at))
        
        return query

# Helper function to create paginator
def get_paginator(session: AsyncSession) -> Paginator:
    """Get paginator instance"""
    return Paginator(session)
