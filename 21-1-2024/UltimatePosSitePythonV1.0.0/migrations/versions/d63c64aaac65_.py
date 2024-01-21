"""empty message

Revision ID: d63c64aaac65
Revises: f352e0865dcc
Create Date: 2023-04-13 05:45:44.851138

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd63c64aaac65'
down_revision = 'f352e0865dcc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('order', sa.Column('tran_ref_to_update', sa.String(length=255), nullable=True))
    op.add_column('order', sa.Column('tran_ref_old', sa.String(length=255), nullable=True))
    op.add_column('order', sa.Column('cs_token_old', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('order', 'cs_token_old')
    op.drop_column('order', 'tran_ref_old')
    op.drop_column('order', 'tran_ref_to_update')
    # ### end Alembic commands ###