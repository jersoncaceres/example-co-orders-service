"""add status to order

Revision ID: f4444f78db26
Revises: a7aaf4e41573
Create Date: 2022-09-07 18:15:29.383038

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f4444f78db26'
down_revision = 'a7aaf4e41573'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('order', sa.Column('status', sa.String(length=64), nullable=True, allow_null=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('order', 'status')
    # ### end Alembic commands ###
