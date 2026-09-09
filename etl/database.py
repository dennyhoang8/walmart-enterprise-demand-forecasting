# ================================
# 1. IMPORT TOOLS
# Load tools for reading environment variables,
# loading the .env file, and connecting to PostgreSQL.
# ================================

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


# ================================
# 2. LOAD ENVIRONMENT VARIABLES
# Read the secret database settings stored
# inside the project's .env file.
# ================================

load_dotenv()


# ================================
# 3. CREATE DATABASE CONNECTION
# Build the PostgreSQL connection information
# using values from the .env file,
# then return a SQLAlchemy database engine.
# ================================

def get_engine() -> Engine:

    # Build the PostgreSQL connection string.
    # os.getenv() gets each database setting
    # from the environment variables loaded above.
    connection_string = (
        f"postgresql+psycopg2://"
        f"{os.getenv('POSTGRES_USER')}:"
        f"{os.getenv('POSTGRES_PASSWORD')}@"
        f"{os.getenv('POSTGRES_HOST')}:"
        f"{os.getenv('POSTGRES_PORT')}/"
        f"{os.getenv('POSTGRES_DB')}"
    )

    # Create and return a SQLAlchemy engine
    # that other Python files can use
    # to communicate with PostgreSQL.
    return create_engine(connection_string)