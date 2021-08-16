import os

from sqlalchemy import create_engine

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
DB_ENGINE = create_engine("sqlite:///" + os.path.join(PROJECT_ROOT, "database.db"))
