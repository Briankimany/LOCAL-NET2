
import os
from pathlib import Path

current_location = os.path.abspath('.')
home_dir = Path(current_location).home()

CONTENT_LOCATION = home_dir /'CONTENT'

DATABASE_LOCATION = CONTENT_LOCATION / "databasev1.db"
USER_DB_LOCATION = CONTENT_LOCATION / "users.db"

UPLOAD_DIR = CONTENT_LOCATION / 'UPLOADS'
UPLOAD_DIR.mkdir(parents=True , exist_ok = True)

ENV_LOCATION = CONTENT_LOCATION / '.env'


DATA_BASE_FILE_TYPES = [['.mp4' , '.mkv','.avi'] ,
                                     ['.zip' , '.tar']]

PROFILES_DIR = CONTENT_LOCATION / 'PROFILE_PICS'
PROFILES_DIR.mkdir(parents = True , exist_ok = True)


