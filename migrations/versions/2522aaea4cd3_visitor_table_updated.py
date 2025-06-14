"""visitor-table-updated

Revision ID: 2522aaea4cd3
Revises: 88e5801166d7
Create Date: 2025-04-06 02:52:56.485052

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2522aaea4cd3'
down_revision = '88e5801166d7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('visitor', schema=None) as batch_op:
        batch_op.add_column(sa.Column('pesel', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('phone_number', sa.String(length=150), nullable=False))
        batch_op.add_column(sa.Column('email', sa.String(length=150), nullable=True))
        batch_op.create_unique_constraint(None, ['pesel'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('visitor', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')
        batch_op.drop_column('email')
        batch_op.drop_column('phone_number')
        batch_op.drop_column('pesel')

    # ### end Alembic commands ###
