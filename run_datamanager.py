from database import DatabaseManager
from databaseutils import clean_db , view_all_tables_and_content

import sqlite3

from config import CONTENT_LOCATION , DATABASE_LOCATION , USER_DB_LOCATION


database_path = DATABASE_LOCATION
database = DatabaseManager(data_base_path=CONTENT_LOCATION)
db_connection = sqlite3.connect(DATABASE_LOCATION)
clean_db(db_connection=db_connection)
database.format_images()
database.generate_db_jsons()
database.update_db_file()
print("\n\n")
view_all_tables_and_content(DATABASE_LOCATION)

print("\n\n")
view_all_tables_and_content(USER_DB_LOCATION)