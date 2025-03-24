"""Changed Models

Revision ID: 1b70faad1931
Revises: d9fa172f307b
Create Date: 2025-03-24 12:41:02.571786

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '1b70faad1931'
down_revision: Union[str, None] = 'd9fa172f307b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop foreign key constraint before dropping the table
    op.drop_constraint('orders_product_id_fkey', 'orders', type_='foreignkey')

    # Drop the column that references the `products` table
    op.drop_column('orders', 'product_id')

    # Now, it's safe to drop the `products` table
    op.drop_table('products')

    # Create the new `produce` table
    op.create_table(
        'produce',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('unit_price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('quality', sa.String(length=50), nullable=False),
        sa.Column('farmer_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['farmer_id'], ['farmers.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Add the new `produce_id` column to `orders`
    op.add_column('orders', sa.Column('produce_id', sa.Integer(), nullable=False))

    # Modify the `order_status` column to be nullable
    op.alter_column('orders', 'order_status',
               existing_type=sa.VARCHAR(length=20),
               nullable=True)

    # Create new foreign key constraint
    op.create_foreign_key('orders_produce_id_fkey', 'orders', 'produce', ['produce_id'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop the new foreign key constraint
    op.drop_constraint('orders_produce_id_fkey', 'orders', type_='foreignkey')

    # Drop the `produce_id` column from `orders`
    op.drop_column('orders', 'produce_id')

    # Recreate the `products` table
    op.create_table(
        'products',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('name', sa.VARCHAR(length=100), autoincrement=False, nullable=False),
        sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True),
        sa.Column('category', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
        sa.Column('unit_price', sa.NUMERIC(precision=10, scale=2), autoincrement=False, nullable=False),
        sa.Column('farmer_id', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(['farmer_id'], ['farmers.id'], name='products_farmer_id_fkey'),
        sa.PrimaryKeyConstraint('id', name='products_pkey')
    )

    # Add the `product_id` column back to `orders`
    op.add_column('orders', sa.Column('product_id', sa.INTEGER(), autoincrement=False, nullable=False))

    # Restore the original foreign key constraint
    op.create_foreign_key('orders_product_id_fkey', 'orders', 'products', ['product_id'], ['id'])

    # Restore the `order_status` column to be NOT NULL
    op.alter_column('orders', 'order_status',
               existing_type=sa.VARCHAR(length=20),
               nullable=False)

    # Drop the `produce` table
    op.drop_table('produce')

