import sqlite3
from pathlib import Path

from utils import get_time , save_load_program_data 


class Users:
    """
    This is a clas to create the users data base
    
    Users.db --> path
        TABLES:
            1. CREDENTIALS
                userid  username  password
                
    """
    def __init__(self , db_folder ,debuging = True) -> None:
        db_path = Path(db_folder)/ "users.db"
        self.debuging = debuging
       
        self.db_path = db_path if isinstance(db_path , Path) else Path(db_path)
        self.LOG_DIR = self.db_path.parent
        # self.LOG_DIR.mkdir(parents=True , exist_ok=True)
        
        db_connection = sqlite3.connect(self.db_path)
        cursor = db_connection.cursor()
        ## initialize the tables if not present
        cursor.execute("CREATE TABLE IF NOT EXISTS CREDENTIALS (userid INTEGER PRIMARY KEY  , username UNIQUE, password)")
        cursor.execute("CREATE TABLE IF NOT EXISTS CONTENT_CONSUMPTION (user_id ,content_id , time)")
        db_connection.commit()
        
        
    def get_cursor(self):
        return sqlite3.connect(self.db_path)
    
    def log(self , query):
        path = self.LOG_DIR /"userquery.json"
        
        if  path.exists():
            current_logs = save_load_program_data(path=path)
        else:
            current_logs ={}
        data =  {get_time():query}
        current_logs.update(data)
        save_load_program_data(path=path , data=current_logs , mode='w')
    
    def add_user(self , username , password):
        """INSERT INTO  SERIES (content_id , item_name ,series_name , image_src ) VALUES (?,?,?,?)", (media_id,name , series_name , image_src)"""
        query = f"INSERT INTO CREDENTIALS (username , password)  VALUES ({username} , {password})"
      
        db_connection=  self.get_cursor()
        cursor = db_connection.cursor()
        cursor.execute("INSERT INTO CREDENTIALS (username , password)  VALUES (?,?)" ,(username, password))
        # cursor.execute(query)
        self.log(query=query)
        db_connection.commit()
            
        # view_all_tables_and_content(self.db_path)
            
        
    
    def get_userid(self , username):
        db_connection = sqlite3.connect(self.db_path)
        cursor = db_connection.cursor()
        query = f"SELECT userid , password FROM CREDENTIALS WHERE username = '{username}'"
        
        details = cursor.execute(query).fetchone()
    
        if details:
            query = f"{query}: RESULTS {details[0]}"
            self.log(query=query)
            return details[0]
        
        else:
            query = f"{query}: RESULTS {details}"
            self.log(query=query)
            return None
    
    def get_password(self, username):
        """
        INPUT: 
            username
        returns :
                password
        """
        user_id = self.get_userid(username=username)
        query = f"SELECT password FROM CREDENTIALS WHERE userid = {user_id}"
        cursor_=  self.get_cursor().cursor() 
        password = cursor_.execute(query).fetchone()
        
        if password:
            password =password[0]
        
        str_q = f"{query}:RESULTS->{password}"
        self.log(query=str_q)
        return password
    
    def update_consumer_table(self,user_id , content_id):
        """TABLE FORMAT
            user id | content id | time
            
            "INSERT INTO CONTENT_CONSUMPTION (user_id, content_id, time) VALUES (?,?,?)"
        """
        db_connection = self.get_cursor()
        cursor = db_connection.cursor()
        time = get_time(string_obj=True)
        query_ = f"INSERT INTO CONTENT_CONSUMPTION (user_id ,content_id , time ) VALUES ({user_id} , {content_id} , {time})"
        query = "INSERT INTO CONTENT_CONSUMPTION (user_id, content_id, time) VALUES (?,?,?)"
        cursor.execute(query, (user_id, content_id, time))
     
        if self.debuging:
            self.log(query=query_)
        db_connection.commit()
        # view_all_tables_and_content(self.db_path)


