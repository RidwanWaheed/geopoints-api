#!/usr/bin/env python3
"""
Script to generate the test directory structure for GeoPoints API
"""

import os
import sys
from pathlib import Path

# Define the test structure
TEST_STRUCTURE = {
    "tests": {
        "__init__.py": "",  # Empty file
        "conftest.py": "# Test fixtures will be defined here\n",
        "README.md": "# GeoPoints API Tests\n\nThis directory contains tests for the GeoPoints API project.\n",
        "test_api": {
            "__init__.py": "",
            "test_points.py": "# Tests for Points API endpoints\n",
            "test_categories.py": "# Tests for Categories API endpoints\n",
            "test_auth.py": "# Tests for Authentication API endpoints\n"
        },
        "test_db": {
            "__init__.py": "",
            "test_point_repo.py": "# Tests for Point repository\n",
            "test_category_repo.py": "# Tests for Category repository\n"
        },
        "test_spatial": {
            "__init__.py": "",
            "test_spatial_queries.py": "# Tests for spatial query functions\n"
        }
    }
}

def create_directories_and_files(base_path, structure):
    """Recursively create directories and files based on the structure dictionary"""
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        
        if isinstance(content, dict):
            # It's a directory
            os.makedirs(path, exist_ok=True)
            print(f"Created directory: {path}")
            create_directories_and_files(path, content)
        else:
            # It's a file
            with open(path, 'w') as f:
                f.write(content)
            print(f"Created file: {path}")

def main():
    # Determine the base directory (project root)
    if len(sys.argv) > 1:
        base_dir = sys.argv[1]
    else:
        # Default to current directory
        base_dir = os.getcwd()
    
    print(f"Creating test structure in: {base_dir}")
    
    # Create the directory structure
    create_directories_and_files(base_dir, TEST_STRUCTURE)
    
    # Create GitHub workflow directory and file
    workflow_dir = os.path.join(base_dir, ".github", "workflows")
    os.makedirs(workflow_dir, exist_ok=True)
    
    workflow_file = os.path.join(workflow_dir, "tests.yml")
    with open(workflow_file, 'w') as f:
        f.write("""name: GeoPoints API Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      # PostgreSQL with PostGIS service
      postgres:
        image: postgis/postgis:15-3.3
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: geopoints_test
        ports:
          - 5432:5432
        # Set health checks to wait until postgres has started
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install pytest pytest-cov
        if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
    
    - name: Run tests
      env:
        TEST_DATABASE_URL: postgresql://postgres:postgres@localhost:5432/geopoints_test
        SECRET_KEY: "testing_secret_key_for_ci_cd_pipeline"
      run: |
        pytest --cov=app tests/
""")
    print(f"Created file: {workflow_file}")
    
    print("\nTest structure created successfully!")
    print("\nNext steps:")
    print("1. Install test dependencies: pip install pytest pytest-cov pytest-asyncio httpx")
    print("2. Implement the test fixtures in conftest.py")
    print("3. Implement your test cases in the respective files")
    print("4. Run your tests with: pytest -v")

if __name__ == "__main__":
    main()