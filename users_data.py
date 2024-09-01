
from users import Users
import config
from database_index import DataBaseIndex
from utils import get_time

import sqlite3
import numpy as np
import pandas as pd



class Result:
    def __init__(self ,id) -> None:
        self.id = id


class UniqueUser(Users):

    def __init__(self, db_folder,user_name :str,debuging=True) -> None:
        super().__init__(db_folder, debuging)

        self.name = user_name.strip()
        root_dir = self.db_path.parent / self.db_path.stem
        self.personal_db = root_dir / self.name/ 'records.db'
        self.CONTENT_LOCATION = config.DATABASE_LOCATION
        self.LOG_DIR = self.personal_db.parent /"LOGS"
        self.LOG_DIR.mkdir(parents=True , exist_ok=True)

        self.verify_in_users()

        self.db_indexer = DataBaseIndex(db_path=config.DATABASE_LOCATION)

        db_connection = sqlite3.connect(self.personal_db)
        cursor = db_connection.cursor()
   
        cursor.execute("CREATE TABLE IF NOT EXISTS CONTENT_CONSUMPTION (content_id INTEGER, time)")
        cursor.execute("CREATE TABLE IF NOT EXISTS PAYED_FOR (id INTEGER , orderid ,date )")
        cursor.execute("CREATE TABLE IF NOT EXISTS CHECK_OUT (orderid, phone,price INTEGER, time,status)")

        db_connection.commit()

    def get_my_userid(self):
        return super().get_userid(username=self.name)
    
    def get_my_password(self):
        return super().get_password(username=self.name)

    def verify_in_users(self):
        all_users = Users(config.CONTENT_LOCATION)
        if all_users.get_userid(self.name):
           pass
        else:
            raise ValueError("IN valid user")
        
    def get_iner_cursor(self , path = None):
        if path:
            return sqlite3.connect(path)
        return sqlite3.connect(self.personal_db)
    

    def update_consumer_table(self, content_id):
        """TABLE FORMAT
             content id | time
            
            "INSERT INTO CONTENT_CONSUMPTION ( content_id, time) VALUES (?,?)"
        """
        db_connection = self.get_iner_cursor()
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
        db_cursor = self.get_iner_cursor(path=self.personal_db)
        query = "SELECT content_id , time FROM CONTENT_CONSUMPTION"
        cursor = db_cursor.cursor()
        results = cursor.execute(query).fetchall()
        # return results
        self.log(query=query)

        tracker = dict(results)
       
        results =sorted(list(tracker.items()))
        
        results = np.array(results)

        return results
    

    def format_user_content(self , json_cont = False):

        results = self.get_user_content_consumption()
        if len(results) == 0:
            return self.get_empty_df()
        content_ids = results[:,0]
        content_types = list(map(self.db_indexer.get_content_type , content_ids))
        content_names = list(map(self.db_indexer.get_content_name , content_ids))
        
        date = results[:,-1]

        results = {"Content ids":content_ids,
                   "type": content_types,
                   "names": content_names,
                   "date":date
                   }
        if json_cont:
            return results
        return pd.DataFrame(results)
    

    def remove_content(self , content_id:int):
        cursor = self.get_iner_cursor()
        cursor.execute("DELETE  FROM CONTENT_CONSUMPTION WHERE content_id = ?", (content_id,))
        cursor.commit()
        cursor.close()


    def get_item_list(self):
        """
        Fetches a list of available items from the database or index.
        Returns a list of item names or IDs.
        """
        # Assuming you can fetch all content from the DataBaseIndex
        all_content_ids = self.get_user_content_consumption()[:,0]
        all_content_names = [self.db_indexer.get_content_name(content_id) for content_id in all_content_ids]
        return all_content_names
    
    def get_empty_df(self):
        return pd.DataFrame({"Content ids":[],
                   "type": [],
                   "names": [],
                   "date":[]
                   })
    
    def get_content_by_id(self , content_id):
        return self.db_indexer.get_content_name(content_id=content_id)


    def update_cart(self , price , status ,  orderid,content_ids , phone , time_initiated , update_payed_for = False):

       
        """UPDATE table_name SET column1 = new_value, column2 = another_new_value WHERE condition;"""
        with self.get_iner_cursor() as cursor:
            if price == None and content_ids == None:
                cursor.execute("UPDATE CHECK_OUT SET status = ? WHERE orderid = ?", (status, orderid))
            else:
                curr_time = get_time()
                if None not in (orderid , price , status , phone , time_initiated):
                    price = int(price)

                    cursor.execute("INSERT INTO CHECK_OUT (orderid, phone, price , time,status) VALUES (? , ? ,?, ?,?)" , (orderid ,phone ,price , time_initiated,status))
                if content_ids != None and orderid !=None and update_payed_for:
                    for i in content_ids:
                        cursor.execute("INSERT INTO PAYED_FOR (id , orderid ,date) VALUES (? , ?,?)" , (i , orderid,curr_time) )

            cursor.commit()
    
    def get_cart_status(self , orderid = None):

        with self.get_iner_cursor() as conn:
            if orderid:
                status = conn.execute(f"SELECT status FROM CHECK_OUT WHERE  orderid = '{orderid}'").fetchone()
            else:
                status = conn.execute(f"SELECT status FROM CHECK_OUT").fetchone()

        if status:
            status= status[0]
        return status
    

    def check_order_details(self , orderid):
        """
        Returns (orderid, phone,price INTEGER, status)
        """

        with self.get_iner_cursor() as conn:
            details  = conn.execute("SELECT * FROM  CHECK_OUT WHERE orderid = ?",(orderid,)).fetchone()

        return {'phone':details[1] , "amount":details[2],'time':details[3],'status':details[4]}
    
    def get_paid_content(self , ids_only = False):
        with self.get_iner_cursor() as conn:
            ids = conn.execute("SELECT id , date FROM PAYED_FOR").fetchall()
        if ids_only:
            ids = [i[0] for i in ids]
        return ids
        
    def classify_payed_cont(self , ids):
        results = {'GAMES':[],"SERIES":{}, 'MOVIES':[]}
        for id  in ids:
            
            cont_type = self.db_indexer.get_content_type(int(id))
            if cont_type == 'GAMES':
                results['GAMES'].append(id)

            if cont_type == "STREAM"  or cont_type == "SERIES":
                cont_path = self.db_indexer.get_full_path(int(id))
    
                if "SERIES" in cont_path:
                    series_name = self.db_indexer.get_series_name(self.db_indexer.get_content_name(id))
                    if series_name not  in  results['SERIES']:
                        results['SERIES'][series_name] = []
                    results['SERIES'][series_name].append(id)
                elif "MOVIES" in cont_path:
                    results["MOVIES"].append(id)

        return results

  

        
