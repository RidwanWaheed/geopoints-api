import os
import sys
import argparse
from alembic import command
from alembic.config import Config 

def main():
    # Create a command-line parser
    parser = argparse.ArgumentParser(description="Create a new Alembic migration")
    parser.add_argument("message", help="Migration message")
    parser.add_argument("--autogenerate", action="store_true", help="Autogenerate migration based on model changes")
    args = parser.parse_args()
    
    # Get the directory where this script is located
    dir_path = os.path.dirname(os.path.realpath(__file__))
    
    # Load the Alembic configuration file
    alembic_cfg = Config(os.path.join(dir_path, "alembic.ini"))
    
    if args.autogenerate:
        # If --autogenerate flag is provided, generate migration automatically
        # This compares your SQLAlchemy models to the current database state
        command.revision(alembic_cfg, args.message, autogenerate=True)
    else:
        # Otherwise, create an empty migration template
        command.revision(alembic_cfg, args.message)
    
    print(f"Migration created with message: {args.message}")

if __name__ == "__main__":
    main()