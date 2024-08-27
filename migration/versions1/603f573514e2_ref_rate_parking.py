"""ref rate_parking

Revision ID: 603f573514e2
Revises: ca0a8ff80dea
Create Date: 2024-08-26 10:00:05.070604

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '603f573514e2'
down_revision: Union[str, None] = 'ca0a8ff80dea'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('parkings', sa.Column('rate_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'parkings', 'rates', ['rate_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'parkings', type_='foreignkey')
    op.drop_column('parkings', 'rate_id')
    # ### end Alembic commands ###