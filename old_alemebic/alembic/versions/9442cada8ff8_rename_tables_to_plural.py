"""rename_tables_to_plural

Revision ID: 9442cada8ff8
Revises: 4f36fddeda68
Create Date: 2025-04-16 23:43:39.287992

"""

import geoalchemy2 as ga
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "9442cada8ff8"
down_revision = "4f36fddeda68"
branch_labels = None
depends_on = None


def upgrade():
    # Rename tables to follow plural convention
    op.rename_table("point", "points")
    op.rename_table("category", "categories")
    op.rename_table("user", "users")


def downgrade():
    # Revert to original names
    op.rename_table("points", "point")
    op.rename_table("categories", "category")
    op.rename_table("users", "user")
