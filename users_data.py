
from users import Users
import config
from database_index import DataBaseIndex
from utils import get_time

import sqlite3
import numpy as np
import pandas as pd

class UniqueUser(Users):

    def __init__(self, db_folder,user_name :str,debuging=True) -> None:
        super().__init__(db_folder, debuging)

        self.name = user_name
        root_dir = self.db_path.parent / self.db_path.stem
        self.personal_db = root_dir / self.name/ 'records.db'
        self.CONTENT_LOCATION = config.DATABASE_LOCATION
        self.db_indexer = DataBaseIndex(db_path=config.DATABASE_LOCATION)

        self.LOG_DIR = self.personal_db.parent /"LOGS"
        self.LOG_DIR.mkdir(parents=True , exist_ok=True)

   
        db_connection = sqlite3.connect(self.personal_db)
        cursor = db_connection.cursor()
   
        cursor.execute("CREATE TABLE IF NOT EXISTS CONTENT_CONSUMPTION (content_id , time)")
        db_connection.commit()

    def get_cursor(self , path = None):
        if path:
            return sqlite3.connect(path)
        return sqlite3.connect(self.personal_db)
    

    def update_consumer_table(self, content_id):
        """TABLE FORMAT
             content id | time
            
            "INSERT INTO CONTENT_CONSUMPTION ( content_id, time) VALUES (?,?)"
        """
        db_connection = self.get_cursor()
        cursor = db_connection.cursor()
        time = get_time(string_obj=True)
        query_ = f"INSERT INTO CONTENT_CONSUMPTION (content_id , time ) VALUES ( {content_id} , {time})"
        query = "INSERT INTO CONTENT_CONSUMPTION ( content_id, time) VALUES (?,?)"
        cursor.execute(query, (content_id, time))
        # cursor.execute(query)
        
        if self.debuging:
            self.log(query=query_)
        db_connection.commit()
        # view_all_tables_and_content(self.personal_db)


    def get_user_content_consumption(self) :
        """
        returns np.array(results)
        """
        db_cursor = self.get_cursor(path=self.personal_db)
        query = "SELECT content_id , time FROM CONTENT_CONSUMPTION"
        cursor = db_cursor.cursor()
        results = cursor.execute(query).fetchall()
        self.log(query=query)
        return np.array(results)
    

    def format_user_content(self):

        results = np.array(self.get_user_content_consumption())

        content_ids = results[:,0]
        content_types = list(map(self.db_indexer.get_content_type , content_ids))
        content_names = list(map(self.db_indexer.get_content_name , content_ids))
        date = results[:,-1]

        results = {"Content ids":content_ids,
                   "type": content_types,
                   "names": content_names,
                   "date":date
                   }
        return pd.DataFrame(results)
    
    def get_item_list(self):
        """
        Fetches a list of available items from the database or index.
        Returns a list of item names or IDs.
        """
        # Assuming you can fetch all content from the DataBaseIndex
        all_content_ids = self.get_user_content_consumption()[:,0]
        all_content_names = [self.db_indexer.get_content_name(content_id) for content_id in all_content_ids]
        return all_content_names


        
