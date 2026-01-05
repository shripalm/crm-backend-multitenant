"""Create payment and subscription system tables (Post-Payment model) in Admin DB

Revision ID: 2345678901c0
Revises: 2345678901bf
Create Date: 2024-12-30 14:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '2345678901c0'
down_revision: Union[str, None] = '2345678901bf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Define reusable PostgreSQL ENUM objects
INVOICE_STATUS_ENUM = postgresql.ENUM(
    'CREATED', 'PAYMENT_PENDING', 'PAID', 'FAILED', 'REFUNDED',
    name='invoice_status',
    metadata=sa.MetaData()
)

PAYMENT_STATUS_ENUM = postgresql.ENUM(
    'INITIATED', 'SUCCESS', 'FAILED', 'PENDING',
    name='payment_status',
    metadata=sa.MetaData()
)


def upgrade() -> None:
    """Create payment and subscription system tables in Admin DB."""
    
    bind = op.get_bind()
    
    # Create ENUM types
    INVOICE_STATUS_ENUM.create(bind, checkfirst=True)
    PAYMENT_STATUS_ENUM.create(bind, checkfirst=True)
    
    # 1. Create crm_payments table (Locked context)
    op.create_table('crm_payments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('order_id', sa.String(length=100), nullable=False),
        sa.Column('txn_id', sa.String(length=100), nullable=True),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('payment_context', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('status', PAYMENT_STATUS_ENUM, nullable=False),
        sa.Column('raw_response', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['agents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('order_id')
    )
    op.create_index(op.f('ix_crm_payments_order_id'), 'crm_payments', ['order_id'], unique=False)
    op.create_index(op.f('ix_crm_payments_status'), 'crm_payments', ['status'], unique=False)
    op.create_index(op.f('ix_crm_payments_user_id'), 'crm_payments', ['user_id'], unique=False)
    
    # 2. Create crm_invoices table (Proof of Payment)
    op.create_table('crm_invoices',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('gen_random_uuid()')),
        sa.Column('invoice_no', sa.String(length=50), nullable=False),
        sa.Column('payment_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('plan_code', sa.String(length=50), nullable=True),
        sa.Column('purpose', sa.String(length=50), nullable=False),
        sa.Column('status', INVOICE_STATUS_ENUM, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['payment_id'], ['crm_payments.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['agents.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('invoice_no'),
        sa.UniqueConstraint('payment_id')
    )
    op.create_index(op.f('ix_crm_invoices_status'), 'crm_invoices', ['status'], unique=False)
    op.create_index(op.f('ix_crm_invoices_user_id'), 'crm_invoices', ['user_id'], unique=False)

    # 3. Create crm_user_subscriptions table
    op.create_table('crm_user_subscriptions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('plan_code', sa.String(length=50), nullable=False),
        sa.Column('start_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['agents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )

def downgrade() -> None:
    # Cleanup in reverse
    op.drop_table('crm_user_subscriptions')
    op.drop_table('crm_invoices')
    op.drop_table('crm_payments')
    
    bind = op.get_bind()
    PAYMENT_STATUS_ENUM.drop(bind, checkfirst=True)
    INVOICE_STATUS_ENUM.drop(bind, checkfirst=True)
