from app.base import Base
from app.database import SessionLocal, engine


def init_db() -> None:
    """Initialize database with tables if they don't exist."""
    # This approach is safer than create_all which can fail on existing objects
    from sqlalchemy import inspect

    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    # Only create tables that don't exist yet
    metadata_tables = Base.metadata.tables.keys()
    tables_to_create = [
        table for table in metadata_tables if table not in existing_tables
    ]

    if tables_to_create:
        # Create only tables that don't exist
        tables_to_create_metadata = Base.metadata.tables_subset(tables_to_create)
        tables_to_create_metadata.create_all(bind=engine)
    else:
        print("All tables already exist, skipping creation")
