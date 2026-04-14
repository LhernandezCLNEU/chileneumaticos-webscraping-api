"""initial

Revision ID: 0001_initial
Revises: 
Create Date: 2026-04-13 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # users
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('email', sa.String(length=255), nullable=False, unique=True, index=True),
        sa.Column('hashed_password', sa.String(length=512), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default=sa.text('1')),
        sa.Column('is_superuser', sa.Boolean(), nullable=True, server_default=sa.text('0')),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )

    # brands
    op.create_table(
        'brands',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=200), nullable=False, unique=True),
    )

    # products
    op.create_table(
        'products',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('sku', sa.String(length=128), nullable=True, index=True),
        sa.Column('title_raw', sa.Text(), nullable=False),
        sa.Column('title_normalized', sa.Text(), nullable=True),
        sa.Column('brand_id', sa.Integer(), sa.ForeignKey('brands.id'), nullable=True),
        sa.Column('specs', sa.JSON(), nullable=True),
        sa.Column('price', sa.Numeric(10, 2), nullable=True),
        sa.Column('currency', sa.String(length=8), nullable=True),
        sa.Column('url', sa.String(length=2000), nullable=True),
        sa.Column('source', sa.String(length=255), nullable=True),
        sa.Column('scraped_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )

    # price_history
    op.create_table(
        'price_history',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('product_id', sa.Integer(), sa.ForeignKey('products.id'), nullable=False, index=True),
        sa.Column('price', sa.Numeric(10, 2), nullable=False),
        sa.Column('currency', sa.String(length=8), nullable=True),
        sa.Column('recorded_at', sa.DateTime(), nullable=True),
    )

    # title_formats
    op.create_table(
        'title_formats',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('pattern', sa.Text(), nullable=False),
        sa.Column('example', sa.Text(), nullable=True),
        sa.Column('priority', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('enabled', sa.Boolean(), nullable=True, server_default=sa.text('1')),
        sa.Column('version', sa.String(length=32), nullable=True),
        sa.Column('created_by_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )

    # tire_specs
    op.create_table(
        'tire_specs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('product_id', sa.Integer(), sa.ForeignKey('products.id'), nullable=False, unique=True),
        sa.Column('width', sa.String(length=16), nullable=True),
        sa.Column('profile', sa.String(length=16), nullable=True),
        sa.Column('diameter', sa.String(length=16), nullable=True),
        sa.Column('load_index', sa.String(length=8), nullable=True),
        sa.Column('speed_rating', sa.String(length=8), nullable=True),
        sa.Column('season', sa.String(length=32), nullable=True),
        sa.Column('tread_pattern', sa.String(length=255), nullable=True),
    )

    # parsed_results
    op.create_table(
        'parsed_results',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('product_id', sa.Integer(), sa.ForeignKey('products.id'), nullable=False),
        sa.Column('title_format_id', sa.Integer(), sa.ForeignKey('title_formats.id'), nullable=True),
        sa.Column('result', sa.JSON(), nullable=True),
        sa.Column('confidence', sa.Integer(), nullable=True),
        sa.Column('parsed_at', sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('parsed_results')
    op.drop_table('tire_specs')
    op.drop_table('title_formats')
    op.drop_table('price_history')
    op.drop_table('products')
    op.drop_table('brands')
    op.drop_table('users')
