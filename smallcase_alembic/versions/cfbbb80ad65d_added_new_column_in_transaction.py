"""Added new column in transaction

Revision ID: cfbbb80ad65d
Revises: d10a16faea20
Create Date: 2021-07-12 15:22:54.402366

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cfbbb80ad65d'
down_revision = 'd10a16faea20'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('transactions', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_transactions_user_id'), 'transactions', ['user_id'], unique=False)
    op.create_foreign_key(None, 'transactions', 'users', ['user_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'transactions', type_='foreignkey')
    op.drop_index(op.f('ix_transactions_user_id'), table_name='transactions')
    op.drop_column('transactions', 'user_id')
    # ### end Alembic commands ###
