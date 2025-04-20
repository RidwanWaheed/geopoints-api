"""add_spatial_indexes

Revision ID: 9ca59e84e612
Revises: 9442cada8ff8
Create Date: 2025-04-17 07:17:24.702836

"""

import geoalchemy2 as ga
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "9ca59e84e612"
down_revision = "9442cada8ff8"
branch_labels = None
depends_on = None


def upgrade():
    # Drop old indexes and create new ones with consistent naming
    op.drop_index("idx_point_geometry", table_name="points", postgresql_using="gist")
    op.drop_index("ix_point_name", table_name="points")

    # Create optimized spatial indexes
    op.create_index(
        "idx_points_geometry",
        "points",
        ["geometry"],
        unique=False,
        postgresql_using="gist",
    )
    op.create_index(
        "idx_points_geography",
        "points",
        [sa.text("geography(geometry)")],
        unique=False,
        postgresql_using="gist",
    )
    op.create_index(op.f("ix_points_name"), "points", ["name"], unique=False)

    # Add the KNN index which isn't supported by SQLAlchemy's autogenerate
    op.execute(
        "CREATE INDEX idx_points_geometry_knn ON points USING GIST (geometry gist_geometry_ops_nd)"
    )

    # Fix category index if needed
    op.drop_index("ix_category_name", table_name="categories")
    op.create_index(op.f("ix_categories_name"), "categories", ["name"], unique=True)


def downgrade():
    # Remove new indexes
    op.drop_index(
        "idx_points_geometry_knn", table_name="points", postgresql_using="gist"
    )
    op.drop_index("idx_points_geography", table_name="points", postgresql_using="gist")
    op.drop_index("idx_points_geometry", table_name="points", postgresql_using="gist")
    op.drop_index(op.f("ix_points_name"), table_name="points")

    # Restore original indexes
    op.create_index(
        "idx_point_geometry",
        "points",
        ["geometry"],
        unique=False,
        postgresql_using="gist",
    )
    op.create_index("ix_point_name", "points", ["name"], unique=False)

    # Restore category index
    op.drop_index(op.f("ix_categories_name"), table_name="categories")
    op.create_index("ix_category_name", "categories", ["name"], unique=True)
