# Database Migrations Guide

This project uses Alembic for database migrations.

## Setup

Ensure your database connection details are correct in your `.env` file.

## Common Migration Tasks

### Creating a New Migration

To create a new migration manually (empty migration):

```bash
python create_migration.py "description_of_changes"
```

To create a new migration manually (empty migration):

```bash
python create_migration.py "description_of_changes" --autogenerate