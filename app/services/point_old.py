"""Create initial tables

Revision ID: 4f36fddeda68
Revises:
Create Date: 2025-04-16 03:11:19.061625

"""

import geoalchemy2 as ga
import sqlalchemy as sa
from sqlalchemy.exc import ProgrammingError

from alembic import op

# revision identifiers, used by Alembic.
revision = "4f36fddeda68"
down_revision = None
branch_labels = None
depends_on = None


def table_exists(tablename):
    """Check if a table exists"""
    conn = op.get_bind()
    result = conn.execute(
        sa.text(
            f"SELECT EXISTS (SELECT FROM pg_tables WHERE tablename = '{tablename}')"
        )
    )
    return result.scalar()


def index_exists(indexname):
    """Check if an index exists"""
    conn = op.get_bind()
    result = conn.execute(
        sa.text(
            f"SELECT EXISTS (SELECT FROM pg_indexes WHERE indexname = '{indexname}')"
        )
    )
    return result.scalar()


def upgrade():
    # Skip the PostGIS extension creation, assume it's already created by a superuser

    # Create category table if it doesn't exist
    if not table_exists("categories"):
        op.create_table(
            "categories",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=100), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("color", sa.String(length=7), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=True,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=True,
            ),
            sa.PrimaryKeyConstraint("id"),
        )

    # Create index on category name if it doesn't exist
    if not index_exists("ix_categories_name"):
        try:
            op.create_index(
                op.f("ix_categories_name"), "categories", ["name"], unique=True
            )
        except Exception:
            pass  # Ignore if it fails (might exist with a different name)

    # Create point table if it doesn't exist
    if not table_exists("points"):
        op.create_table(
            "points",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=100), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column(
                "geometry",
                ga.types.Geometry(
                    geometry_type="POINT",
                    srid=4326,
                    from_text="ST_GeomFromEWKT",
                    name="geometry",
                    nullable=False,
                ),
                nullable=False,
            ),
            sa.Column("category_id", sa.Integer(), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=True,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=True,
            ),
            sa.ForeignKeyConstraint(
                ["category_id"],
                ["category.id"],
            ),
            sa.PrimaryKeyConstraint("id"),
        )

    # Create index on point name if it doesn't exist
    if not index_exists("ix_points_name"):
        try:
            op.create_index(op.f("ix_points_name"), "points", ["name"], unique=False)
        except Exception:
            pass  # Ignore if it fails

    # Create spatial index if it doesn't exist
    if not index_exists("idx_points_geometry"):
        try:
            op.create_index(
                "idx_points_geometry",
                "points",
                ["geometry"],
                unique=False,
                postgresql_using="gist",
            )
        except Exception:
            pass  # Ignore if it fails

    # Create spatial index if it doesn't exist
    if not index_exists("idx_points_geography"):
        try:
            op.create_index(
                "idx_points_geography",
                "points",
                [sa.text("geography(geometry)")],
                unique=False,
                postgresql_using="gist",
            )
        except Exception:
            pass  # Ignore if it fails

    # Create spatial index if it doesn't exist
    if not index_exists("idx_points_geography"):
        try:
            "CREATE INDEX idx_points_geometry_knn ON points USING GIST (geometry gist_geometry_ops_nd)"
        except Exception:
            pass  # Ignore if it fails


def downgrade():
    # Try to drop everything, ignore errors
    try:
        op.drop_index(op.f("ix_point_name"), table_name="point")
    except Exception:
        pass

    try:
        op.drop_index("idx_point_geometry", table_name="point")
    except Exception:
        pass

    try:
        op.drop_table("point")
    except Exception:
        pass

    try:
        op.drop_index(op.f("ix_category_name"), table_name="category")
    except Exception:
        pass

    try:
        op.drop_table("category")
    except Exception:
        pass
