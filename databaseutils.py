

from pathlib import Path
from utils import convert_dict , save_load_program_data , get_max_dict , compare
import os

import sqlite3
import os



def determine_content_type(content_path):
    categories = ['GAMES' , 'MOVIES' , 'STREAM' , 'SERIES']

    if categories[2] in content_path:
            return categories[2]

    for category in categories:
        if category in content_path and categories[2] not in content_path:
            return category



def get_files_patterns(source_dir , file_types):
    """
    This function takes a source directory path (`source_dir`) and a list of file extensions (`file_types`) as input.

    It searches the source directory for files matching the specified file types and separates them into two categories:

    - Content profile files: These are files with extensions `.png`, `.jpg`, or `.jpeg`.
    - Other content files: These are files with extensions specified in the `file_types` list.

    The function returns a tuple containing two lists:

    - The first list contains paths to all content profile files (`.png`, `.jpg`, `.jpeg`).
    - The second list contains paths to all other content files with extensions specified in `file_types`.
    """

    source_dir = source_dir if isinstance(source_dir , Path) else Path(source_dir)
    content_profile = list(source_dir.glob("*.png")) + list(source_dir.glob("*.jpg")) + list(source_dir.glob("*.jpeg"))
    # print("\n")
    directories = os.listdir(source_dir)


    content_files =[]
    for file_type in file_types:
        data = source_dir.glob(f"*{file_type}")
        content_files.extend(data)

    ruler = content_files
    follow = content_profile

    if len (content_profile) >  len(content_files):
        ruler = content_profile
        follow = content_files

    elif len(content_files) == len(content_profile):
        pass

    result_dict = {}

    if len(content_files) == 0 and len(content_profile) > 0:
        content_files = [(Path(i).with_suffix(".zip")).absolute() for i in content_profile]

    if source_dir.name == "GAMES" :
        additional_files =  [Path((source_dir/i)) for i in os.listdir(source_dir)  if Path((source_dir/i)).is_dir()]
        # print(additional_files)
        content_files.extend(additional_files)
       
    return content_files , content_profile


def determine_ruler_follower_save_recurse( directory ,content_files, content_profile ):
    """
    This function analyzes the content of a directory based on two lists of paths:

    - `content_files`: A list of paths to files with extensions specified in `prepare_data_base_jsons`.
    - `content_profile`: A list of paths to files with extensions `.png`, `.jpg`, or `.jpeg`.

    It determines four flags based on the content:

    - `ruler`: A list of paths that will be used as a reference for comparison (initially set to `content_files`).
    - `follow`: A list of paths that will be compared against the `ruler` (initially set to `content_profile`).
    - `recurse`: A boolean flag indicating whether to process subdirectories (initially set to `False`).
    - `save`: A boolean flag indicating whether to save data to a JSON file (initially set to `True`).

    The function sets these flags based on the following logic:

    - If both lists are empty, `save` is set to `False` (no data to save).
    - If `content_profile` is smaller and `content_files` exist, `ruler` and `follow` are swapped (use content profile as reference).
    - If `content_files` are empty or both lists are empty, `recurse` is set to `True` to explore subdirectories. In this case, `ruler` is populated with subdirectory paths using `os.listdir`.

    The function returns a tuple containing `ruler`, `follow`, `recurse`, and `save` flags.
    """

    recurse = False
    save = True
    ruler = content_files
    follow = content_profile
    if (len(content_files) == 0 and len(content_profile) ==0):
        save = False

    if len (content_profile) >  len(content_files)  and len(content_files) > 0:
        ruler = content_profile
        follow = content_files

    elif len(content_files) ==0 and len(content_profile) > 0 or (len(content_files) == 0 and len(content_profile) ==0) and "GAMES" not in str(directory):
        recurse = True
        ruler =[]
        for file in os.listdir(directory):
            file = os.path.join(directory , file)
            if  Path(file).is_dir():
                ruler.append(Path(file))

    return ruler , follow , recurse , save



def save_data_base_json(result_dict  , source_dir , debuging , tracker_name = "tracker.json"):

    """
    Saves a dictionary (`result_dict`) containing processed data to a JSON file
    within the specified directory (`source_dir`).

    Args:
        result_dict (dict): The dictionary containing the data to be saved.
        source_dir (Path): The path to the directory where the JSON file will be saved.
        debuging (bool, optional): Enables debug mode, which saves a copy of
            the dictionary with a different filename (defaults to False).
        tracker_name (str, optional): The filename for the JSON file to be saved
            (defaults to "tracker.json").

    Returns:
        None

    This function performs the following steps:

    1. Constructs the path to the JSON file using `source_dir` and `tracker_name`.
    2. Handles debugging mode (if enabled):
        - Creates a copy of the `result_dict` to avoid modifying the original.
        - Converts the dictionary to a string representation using `convert_dict`
          (assuming `convert_dict` is defined elsewhere).
        - Saves the string representation to a temporary JSON file named "test.json"
          within the `source_dir`.
    3. Checks if the target JSON file (`tracker.json`) already exists:
        - If it exists:
            - Loads the existing data using `save_load_program_data` (assuming it's defined elsewhere).
            - Converts the loaded data using `convert_dict` (assuming it's defined elsewhere).
            - Uses `get_max_dict` (assuming it's defined elsewhere) to determine
              which dictionary has "more" data based on your specific criteria.
            - Updates the final dictionary based on the comparison result:
                - If `present_dict` has "more" data, it is updated with `result_dict`.
                - Otherwise, `result_dict` is updated with `present_dict`.
        - If the file doesn't exist, the `result_dict` is used as the final dictionary.
    4. Saves the final dictionary to the target JSON file (`tracker.json`) using
        `save_load_program_data` (assuming it converts data to a string before saving).

    """

    dict_path = source_dir / tracker_name
    if debuging:
        debuging_name = "test.json"
        save_load_program_data(path=(source_dir/debuging_name) , data= convert_dict(result_dict.copy() , to_string=True) , mode='w')


    final_d = result_dict
    save_load_program_data(path=dict_path , data = convert_dict(final_d ,to_string=True) , mode = "w")




def prepare_data_base_jsons(directory , file_types = [".mp4"] , debuging = False):

    """
    Prepare and generate tracker JSON files based on the directory content.

    Args:
        directory (Path): The source directory.
        file_types (list, optional): List of file types to include. Defaults to [".mp4"].
        debugging (bool, optional): Flag to enable debugging mode. Defaults to False.

    """
    source_dir = directory if isinstance(directory , Path) else Path(directory)
    # print("getinf info from ", directory , file_types)
    content_files , content_profile = get_files_patterns(source_dir=source_dir , file_types = file_types)
    # print("here sre the content and content profilr", content_files , content_profile)
    ruler , follow , recurse , save    = determine_ruler_follower_save_recurse( directory= source_dir,
                                                                               content_files=content_files ,
                                                                               content_profile=content_profile)

    result_dict = compare(ruler=ruler , follow=follow)
    # print("here is result dit",result_dict , "from this dir" , directory)
    dict_name ="tracker.json"
    if recurse:
        dict_name = "redirect.json"
    if save:
        save_data_base_json(result_dict=result_dict,
                            source_dir=source_dir,
                            debuging=debuging , tracker_name=dict_name)

    if recurse:
        for inner_dir in ruler:
            prepare_data_base_jsons(directory=inner_dir , file_types=file_types)


def view_all_tables_and_content(db_filename):
    # Connect to the database
    connection = sqlite3.connect(db_filename)
    cursor = connection.cursor()

    # Get a list of all tables in the database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()

    # Loop through each table
    for table in tables:
        table_name = table[0]
        # print(table_name)
        # print_table_content(db_filename=db_filename, table_name=table)
        print(f"Table: {table_name}")

        # Retrieve all rows from the table
        cursor.execute(f"SELECT * FROM '{table_name}'")
        rows = cursor.fetchall()

        # Print each row
        if rows:
            print("Content:")
            for row in rows:
                print(row)
        else:
            print("Table is empty")

        print("\n")  # Add a newline between tables

    # Close the connection
    connection.close()


def create_database(db_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    # print("adding talaes , to" , db_file)
    cursor.execute("""CREATE TABLE IF NOT EXISTS FULL_TABLE (content_id , category ,downloadable)""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS SHORT_TABLE (id INTEGER PRIMARY KEY , item_name  ,destination , image_src)""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS MOVIES (content_id INTEGER , item_name , image_src )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS SERIES (content_id INTEGER , item_name , series_name , image_src)""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS GAMES (content_id  INTEGER, item_name , image_src)""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS NO_PROFILES (content_id INTEGER  , item_name)""")

    conn.commit()
    conn.close()


def validate_not_in_db(cursor, destination):
    not_in_data_base = cursor.execute(f"SELECT destination FROM SHORT_TABLE WHERE destination = ?",(destination,)).fetchone() == None
    return not_in_data_base


def insert_media(db_connnection, category , name,downloadable ,destination , image_src):
    # print("calling the insert method")
    cursor = db_connnection.cursor()
    # insert the coontent and get an id
    cursor.execute("INSERT INTO  SHORT_TABLE (item_name  ,destination , image_src) VALUES (?,?,?)", (name,destination , image_src))
    media_id = cursor.execute("SELECT id FROM SHORT_TABLE WHERE  item_name = ?" ,(name,))
    media_id = media_id.fetchone()[0]

    ## insert in full table
    cursor.execute("INSERT INTO  FULL_TABLE (content_id , category ,downloadable) VALUES (?,?,?)", (media_id,category,downloadable))
    if "SERIES" in destination:
        series_name = Path(destination).parent.name
        if series_name == category:
            print("You need to put this in a seson folder but settin the name of series to somethin you wont like" ,series_name )
            series_name = Path(destination).name

        cursor.execute("INSERT INTO  SERIES (content_id , item_name ,series_name , image_src ) VALUES (?,?,?,?)", (media_id,name , series_name , image_src))

    elif "MOVIES" in destination:
        cursor.execute("INSERT INTO  MOVIES (content_id , item_name, image_src ) VALUES (?,?,?)", (media_id,name , image_src))
    elif "GAMES" in destination:
        cursor.execute("INSERT INTO  GAMES (content_id , item_name , image_src ) VALUES (?,?,?)", (media_id,name , image_src))

    if image_src == None or image_src=="None":
         cursor.execute("INSERT INTO  NO_PROFILES (content_id , item_name ) VALUES (?,?)", (media_id,name))

    db_connnection.commit()


#  cursor.execute("UPDATE SHORT_TABLE SET destination = ?, image_src = ? WHERE item_name = ?", (destination, image_src, name))
def modyfy_db(db_connnection:sqlite3.Cursor, category , name,downloadable ,destination , image_src):
    cursor = db_connnection.cursor()
    # insert the coontent and get an id
    # print("calling the imodify method")
    media_id = cursor.execute("SELECT id FROM SHORT_TABLE WHERE  destination = ?" ,(destination,))
    media_id = media_id.fetchone()[0]
    cursor.execute("UPDATE SHORT_TABLE SET item_name = ? , destination =?, image_src=? WHERE id = ?", (name,destination , image_src , media_id))

    ## insert in full table
    # cursor.execute("INSERT INTO  FULL_TABLE (content_id , category ,downloadable) VALUES (?,?,?)", (media_id,category,downloadable))
    cursor.execute("UPDATE FULL_TABLE SET  category =?, downloadable =?  WHERE content_id = ?", (category,downloadable,media_id))
    # print("in mofify" , destination , image_src)
    if "SERIES" in destination:
        root_folder = Path(destination).parent
        series_name = Path(destination).parent.name
        if series_name == category:
            # print("You need to put this in a seson folder but settin the name of series to somethin you wont like" ,series_name )
            series_name = Path(destination).name



        # cursor.execute("INSERT INTO  SERIES (content_id , item_name ,series_name , image_src ) VALUES (?,?,?,?)", (media_id,name , series_name , image_src))
        cursor.execute("UPDATE SERIES SET  item_name =?, series_name=?  , image_src=?  WHERE content_id = ?", (name , series_name,image_src , media_id))

    elif "MOVIES" in destination:
        # cursor.execute("INSERT INTO  MOVIES (content_id , item_name, image_src ) VALUES (?,?,?)", (media_id,name , image_src))
        cursor.execute("UPDATE MOVIES SET  item_name =?, image_src=?  WHERE content_id = ?", (name , image_src , media_id))

    elif "GAMES" in destination:
        # cursor.execute("INSERT INTO  GAMES (content_id , item_name , image_src ) VALUES (?,?,?)", (media_id,name , image_src))
        # print("Updating the src image for games in modify" , image_src , destination)
        cursor.execute("UPDATE GAMES SET  item_name =?, image_src=?  WHERE content_id = ?", (name , image_src , media_id))


    if image_src == None or image_src == "None":
        # print("mofifyin " , destination , name , image_src , media_id)
        added_ids = cursor.execute("SELECT content_id FROM NO_PROFILES").fetchall()
        if (media_id,) in added_ids:
            cursor.execute("UPDATE NO_PROFILES SET  item_name =? WHERE content_id = ?", (name ,  media_id))
        else:
            cursor.execute("INSERT INTO  NO_PROFILES (content_id , item_name ) VALUES (?,?)", (media_id,name))


    else:
        added_ids = cursor.execute("SELECT content_id FROM NO_PROFILES").fetchall()
        if (media_id,) in added_ids:
            # print("This was in no profiles but got removed" , name , media_id , destination)
            cursor.execute("DELETE FROM NO_PROFILES WHERE content_id =?", (media_id,))

    db_connnection.commit()



def clean_db(db_connection:sqlite3.connect ):
    cursor = db_connection.cursor()
    """
    remove files which are not present
        SHORT_TABLE FULL_TABLE , SERIES , MOVIES GAMES NO_PROFILES
        GET CONTENT_ID FROM SHORT TABLE AND REMOVE IT FROM FROM THE REST OF THE TABLES
    """
    # print("caling tje clean funtion")
    def remove(db_connection , table_name , content_id):
        column = "content_id" if not table_name == "SHORT_TABLE" else "id"
        cursor = db_connection.cursor()
        query = f"DELETE FROM {table_name} WHERE {column} ={content_id}"
        # print(query)
        cursor.execute(query)
        db_connection.commit()

    tables_to_check = ["SHORT_TABLE" ,"FULL_TABLE" , "SERIES" , "MOVIES" ,"GAMES", "NO_PROFILES"]
    query = f"SELECT id ,destination FROM SHORT_TABLE"
    content_ids = cursor.execute(query).fetchall()
    # print("here are the content ids")
    for content_id , destination in content_ids:
        # print("evaluationg if it exists  " , destination)
        if Path(destination).exists():
            continue
        else:
            # print(destination)
            for table_name in tables_to_check:
                # print("caling the remove thing on" , table_name ,content_id)
                remove(db_connection=db_connection , table_name=table_name , content_id=content_id)



def print_table_content(db_filename = None, table_name = 'Pricing'):

    if db_filename:
        # Connect to the database
        connection = sqlite3.connect(db_filename)
        cursor = connection.cursor()

    # Retrieve all rows from the specified table
    cursor.execute(f"SELECT * FROM '{table_name}'")
    rows = cursor.fetchall()

    # Print table header
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [col[1] for col in cursor.fetchall()]
    print(" | ".join(columns))
    print("-" * (len(" | ".join(columns))))

    # Print each row
    for row in rows:
        print("\t|".join(map(str, row)))
    if db_filename:
        connection.close()


def update_db(db_conection:sqlite3.connect,  tracker_jsons ):
    data =[]
    cursor =db_conection.cursor()

    for file in tracker_jsons:
        content = save_load_program_data(file)
        for  content_data ,image_profile  in content.items():
            if  Path(content_data).suffix not in ['.jpg' , '.png']:

                if Path(content_data).is_file() :
                    name = Path(content_data).stem
                else:
                    name = str(Path(content_data).stem )+ "_WAITING"

                category = content_data.split(os.sep)[1]
                category = determine_content_type(content_data)
                # print(f"Here is the content data {content_data} , {content_data.split(os.sep)}")
                downloadable = True
                if category == "STREAM":
                    downloadable = False
                info = category , name , downloadable , content_data , image_profile
                data.append(info)
            else:
                print(f"cant satisfy to add this {content_data , image_profile} to the db")

    for info in data:
        category , name,downloadable ,destination , image_src = info
        # print ("here is item" , info , "\n")
        if "SERIES" in destination:
            series_source_dir = Path(destination).parent
            image_src =series_source_dir.with_suffix(".jpg")
            if image_src.is_file():
                image_src = str(image_src)
            else:
                image_src = None

        not_in_data_base = validate_not_in_db(cursor=cursor,destination=destination)
        if image_src =="None":
                image_src == None
        if not_in_data_base:
            insert_media(db_connnection=db_conection,
                         name=name,category=category,
                         downloadable=downloadable,
                         destination=destination ,
                         image_src=image_src)
        else:
            modyfy_db(db_connnection=db_conection,
                      name=name , category=category ,
                      downloadable=downloadable,
                      destination=destination,image_src=image_src)














