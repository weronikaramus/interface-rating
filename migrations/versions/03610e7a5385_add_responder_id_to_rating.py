"""Add responder_id to Rating

Revision ID: 03610e7a5385
Revises: 677875e2f31f
Create Date: 2024-06-13 19:26:06.839293

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '03610e7a5385'
down_revision = '677875e2f31f'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('rating') as batch_op:
        batch_op.add_column(sa.Column('responder_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_responder_rating', 'responder', ['responder_id'], ['id'])

def downgrade():
    with op.batch_alter_table('rating') as batch_op:
        batch_op.drop_constraint('fk_responder_rating', type_='foreignkey')
        batch_op.drop_column('responder_id')

    # ### end Alembic commands ###
