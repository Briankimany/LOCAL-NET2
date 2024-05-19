
import os
from pathlib import Path

current_location = os.path.abspath('.')
home_dir = Path(current_location).home()

CONTENT_LOCATION = home_dir /'CONTENT'

DATABASE_LOCATION = CONTENT_LOCATION / "databasev1.db"
USER_DB_LOCATION = CONTENT_LOCATION / "users.db"


ENV_LOCATION = CONTENT_LOCATION / '.env'

