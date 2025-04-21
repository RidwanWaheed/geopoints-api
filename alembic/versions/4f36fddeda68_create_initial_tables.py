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
    conn = op.get_bind()

    # Create PostGIS extension
    if not conn.execute(
        sa.text("SELECT 1 FROM pg_extension WHERE extname = 'postgis'")
    ).scalar():
        try:
            op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
        except Exception as e:
            print(f"Warning: Could not create PostGIS extension: {e}")
            print("You may need to create it manually with superuser privileges")

    # Create categories table
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
        op.create_index(op.f("ix_categories_name"), "categories", ["name"], unique=True)

    # Create points table
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
                ["categories.id"],
            ),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_points_name"), "points", ["name"], unique=False)

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

        if not index_exists("idx_points_geometry_knn"):
            try:
                op.execute(
                    "CREATE INDEX idx_points_geometry_knn ON points USING GIST (geometry gist_geometry_ops_nd)"
                )
            except Exception:
                pass  # Ignore if it fails

    # Create users table
    if not table_exists("users"):
        op.create_table(
            "users",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("email", sa.String(), nullable=False),
            sa.Column("username", sa.String(), nullable=False),
            sa.Column("hashed_password", sa.String(), nullable=False),
            sa.Column("is_active", sa.Boolean(), server_default="true", nullable=True),
            sa.Column(
                "is_superuser", sa.Boolean(), server_default="false", nullable=True
            ),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("timezone('UTC', CURRENT_TIMESTAMP)"),
                nullable=True,
            ),
            sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_users_email", "users", ["email"], unique=True)
        op.create_index("ix_users_username", "users", ["username"], unique=True)

    # Add the distance calculation function
    if not function_exists("calculate_distance"):
        op.execute(
            """
            CREATE OR REPLACE FUNCTION calculate_distance(
                point_geom GEOMETRY,
                lat DOUBLE PRECISION,
                lng DOUBLE PRECISION
            ) RETURNS DOUBLE PRECISION AS $$
            BEGIN
                RETURN ST_Distance(
                    point_geom::geography,
                    ST_SetSRID(ST_MakePoint(lng, lat), 4326)::geography
                );
            END;
            $$ LANGUAGE plpgsql IMMUTABLE
            """
        )


def function_exists(function_name):
    """Check if a function exists"""
    conn = op.get_bind()
    result = conn.execute(
        sa.text(
            f"SELECT EXISTS (SELECT FROM pg_proc WHERE proname = '{function_name}')"
        )
    )
    return result.scalar()


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
