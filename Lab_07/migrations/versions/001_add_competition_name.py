"""Додавання стовпця competition_name до таблиці results

Revision ID: 001_add_competition_name
Revises: 
Create Date: 2026-11-18 19:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "001_add_competition_name"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)
    cols = [c["name"] for c in insp.get_columns("results")]
    if "competition_name" not in cols:
        with op.batch_alter_table("results", schema=None) as batch_op:
            batch_op.add_column(
                sa.Column("competition_name", sa.String(length=200), nullable=True)
            )


def downgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)
    cols = [c["name"] for c in insp.get_columns("results")]
    if "competition_name" in cols:
        with op.batch_alter_table("results", schema=None) as batch_op:
            batch_op.drop_column("competition_name")
