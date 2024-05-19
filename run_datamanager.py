

from database import DatabaseManager
from databaseutils import clean_db , view_all_tables_and_content
from users import Users
import sqlite3
database_path = "content2"
database = DatabaseManager(data_base_path=database_path)
db_connection = sqlite3.connect("content2/databasev1.db")
# clean_db(db_connection=db_connection)
database.format_images()
database.generate_db_jsons()
database.update_db_file(json_source="content2")
view_all_tables_and_content("content2/databasev1.db")