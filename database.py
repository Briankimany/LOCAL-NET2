
from pathlib import Path
from PIL import Image
from utils import save_load_program_data
import os


from databaseutils import prepare_data_base_jsons
from databaseutils import view_all_tables_and_content
from databaseutils import create_database, update_db , view_all_tables_and_content , clean_db
import sqlite3

from pathlib import Path
from utils import get_time


class DatabaseManager:
    """
    root folder
        |--- movies ---> contains free singke movies
        |--- games --->  contains games
        |--- series ---> contain free series
        |--- stream ---> contains non-free series and movies
                |--- single movies
                |--- series

    """
    def __init__(self , data_base_path ,  data_base_design = None) -> None:
        self.data_base_path = Path(data_base_path)
        self.root_dir = self.data_base_path
        # self.changed_data  = self.data_base_path / 'CHANGED_DATA.json'
        self.root_dir.mkdir(exist_ok=True , parents=True)

        self.data_base_file_types = [['.mp4' , '.mkv','.avi'] ,
                                     ['.zip']]
        self.full_paths = {}
        self.default_design = data_base_design if data_base_design else self.get_default_design()
        self.data_base_json_design = self.data_base_path /"DATA_BASE_DESIGN.json"
        self.FULL_NAMES_JOINED_DICT_path = Path("FULL_NAMES_JOINED_DICT.json")

        self.db_root = self.data_base_path/"databasev1.db"
         ## load the FULL_NAMES_JOINED_DICT.json if it exists or set it to empty
        self.FULL_NAMES_JOINED_DICT = save_load_program_data(path=self.FULL_NAMES_JOINED_DICT_path) if self.FULL_NAMES_JOINED_DICT_path.is_file() else {}

        if not self.db_root.is_file():
            self.db_root.parent.mkdir(parents=True , exist_ok=True)
        create_database(self.db_root)

    def format_images(self , desired_size = (256 , 256)):
        images_paths = []
        images_ext = ['.jpg' , '.webp' , '.png' , '.jpeg']
        for ext  in images_ext:
            found_images = list(self.data_base_path.rglob(f"*{ext}"))
            # print(found_images , ext)
            images_paths.extend(found_images)


        def rename_image(image_path:Path , universal_ext = '.jpg'):
            if image_path.suffix != universal_ext:
                target_path = image_path.absolute().with_suffix(universal_ext)
                image_path = image_path.rename(target=target_path)
            return image_path

        def resize_image(image_path:Path , size = desired_size , universal_ext = '.jpg'):
            if image_path.exists():
                image_path = rename_image(image_path=image_path , universal_ext=universal_ext)
                image  = Image.open(image_path)
                image = image.resize(size=size)
                image.save(fp = image_path)

            return image_path

        # print(images_paths)
        formated_images = list(map(resize_image , images_paths))

        return formated_images

    def get_default_design(self):
        design = {
            "MOVIES":{},
            "GAMES":{},
            "SERIES":{},
            "STREAM" :{"MOVIES" :{},
                       "SERIES" :{}
                       }
            }

        return design

    def create_data_base_design(self,default_state) -> dict:
        for directory in default_state:
            child_dirs = default_state[directory].keys()
            full_path = os.path.join(self.root_dir ,directory)
            if len(list(child_dirs)) ==0:
                self.full_paths[directory]= full_path

            elif len(list(child_dirs)) > 0:
                child_dict = dict([(os.path.join(directory,child_dir) , default_state[directory][child_dir]) for index , child_dir in enumerate(child_dirs)])
                self.create_data_base_design(child_dict)
        return self.full_paths

    def get_data_base_design(self):
        root_dir = self.data_base_path
        design = {}
        for root, dirs, files in os.walk(root_dir):
            current_dir = os.path.relpath(root, root_dir)
            current_dict = design
            for component in current_dir.split(os.sep):
                current_dict = current_dict.setdefault(component, {})
            for file in files:
                current_dict[file] = {}
        return design

    def generate_db_jsons(self):
        data_base_design = self.create_data_base_design(default_state=self.default_design)
        save_load_program_data(path=self.data_base_json_design , data=data_base_design , mode='w')
        for _ , path in data_base_design.items():
            print("Evaluating tis" , path)
            path = Path(path)
            if path.exists():
                continue
            else:
                path.mkdir(parents=True)

        for name ,folder in data_base_design.items():
            folder = Path(folder)
            if "MOVIES" in str(folder) or "SERIES" in str(folder):
                file_types = ['.mp4' , '.mkv']
            elif "GAMES" in str(folder):
                file_types =['.zip']
            else:
                raise ValueError("invalid file format in" , folder)

            prepare_data_base_jsons(directory=folder , file_types=file_types , debuging=False)

    def update_db_file(self , json_source = None):

        source_path = Path(json_source) if json_source else self.data_base_path
        json_trackers = list(source_path.rglob("tracker.json"))
        print("Got some files" , json_trackers , "from" , source_path)
        db_connection = sqlite3.connect(self.db_root)
        update_db(db_conection=db_connection , tracker_jsons=json_trackers)
        db_connection = sqlite3.connect(self.db_root)
        # clean_db(db_connection=db_connection)
        db_connection.commit()
        db_connection.close()






class DataBaseIndex:


    def __init__(self , db_path) -> None:
        self.root_dir = Path(db_path).absolute()
        self.db = sqlite3.connect(self.root_dir)



    def log(self , query:str):
        log_path = self.root_dir.parent /f"{self.root_dir.name}.LOGS.json"
        if log_path.is_file():
            data = save_load_program_data(path = log_path)
            data.update({get_time():query})
        else:
            data = {get_time():query}
        save_load_program_data(path=log_path , data=data , mode='w')


    def get_movies(self , NAME = None , all= False):
        NAME = self.clean_name(NAME)
        db =sqlite3.connect(self.root_dir)
        cursor = db.cursor()
        """
        returns [(content_id , item_name , image_src)]
        """
        cursor = db.cursor()

        if NAME != "MOVIES":
            movies_query = f"SELECT content_id , item_name ,image_src FROM MOVIES WHERE item_name = '{NAME}'"
        else:
            movies_query = f"SELECT content_id , item_name , image_src FROM MOVIES"

        movies = list(cursor.execute(movies_query).fetchall())

        if all:
            movies_copy= movies
        else:
            movies_copy = []
            for i in movies:
                movie_id , item_name , image_src  =i
                # print(self.determine_if_downloadable(series_id) , series_id , i[0:2])
                if self.determine_if_downloadable(movie_id) and (image_src != None and image_src != "None"):
                    movies_copy.append(i)
                else:
                    pass
            cursor.close()

        self.log(query=movies_query)
        return movies_copy

    def clean_name(self , name):
        if isinstance(name , (tuple , list)):
            return name[0]
        return name

    def filter_content(self,names , premium):
        results =[]
        for content_id , name , image_src in names:
            content_id = self.get_content_id(name)
            if self.determine_if_downloadable(content_id=content_id) == premium:
                results.append((content_id , name , image_src))



    def get_series(self , NAME , all= False):
        db =sqlite3.connect(self.root_dir)
        cursor = db.cursor()
        NAME = self.clean_name(NAME)
        """
        returns [(content_id , item_name , image_src)]
        """

        if NAME != "SERIES":
            series_query = f"SELECT content_id , item_name ,image_src FROM SERIES WHERE item_name = '{NAME}'"
        else:
            series_query = f"SELECT content_id , item_name ,image_src FROM SERIES"

        series = list(cursor.execute(series_query).fetchall())

        if all:
            series_copy= series
        else:
            series_copy = []
            for i in series:
                series_id , item_name ,image_src =i
                # print(self.determine_if_downloadable(series_id) , series_id , i[0:2])
                if self.determine_if_downloadable(series_id) and (image_src != None and image_src != "None"):
                    if i not in series_copy:
                        series_copy.append(i)
                    continue
                else:
                    pass
            cursor.close()

        self.log(query=series_query)
        return series_copy

    def get_game(self , NAME):
        NAME = self.clean_name(NAME)
        """
        returns [(content_id , item_name , image_src)]
        """

        cursor =sqlite3.connect(self.root_dir).cursor()

        if NAME != "GAMES":
            game_query = f"SELECT content_id , item_name ,image_src FROM GAMES WHERE item_name = '{NAME}'"
        else:
            game_query = f"SELECT content_id , item_name , image_src FROM GAMES"

        games = list(cursor.execute(game_query).fetchall())
        cursor.close()
        self.log(query=game_query)
        return games


    def get_full_path(self , content_id):
        """
        returns (str(destination))
        """
        db =sqlite3.connect(self.root_dir)
        cursor = db.cursor()
        query = f"SELECT destination FROM SHORT_TABLE WHERE id = {content_id}"
        destination = cursor.execute(query).fetchone()[0]
        db.close()

        return destination

    def get_content_type(self , content_id):
        """
        returns content type eg MOVIES , SERIES , GAMES ...
        """
        cursor = sqlite3.connect(self.root_dir).cursor()
        content_type = cursor.execute(f"SELECT category FROM FULL_TABLE WHERE content_id = {content_id}").fetchone()

        if content_type:
            content_type = content_type[0]
        return content_type

    def determine_if_downloadable(self , content_id):
        """
        return True or false
        """
        db = sqlite3.connect(self.root_dir)
        cursor = db.cursor()
        query = f"SELECT downloadable FROM FULL_TABLE WHERE content_id = {content_id}"
        int_downloadable =   cursor.execute(query).fetchone()[0]
        return bool(int(int_downloadable))


    def get_content_id(self , name):
        cursor = sqlite3.connect(self.root_dir).cursor()
        content_id = cursor.execute(f"SELECT id FROM SHORT_TABLE WHERE item_name = '{name}'").fetchone()[0]
        return content_id


    def get_content_name(self , content_id):
        cursor = sqlite3.connect(self.root_dir).cursor()
        name = cursor.execute(f"SELECT item_name FROM SHORT_TABLE WHERE id = {content_id}").fetchone()
        if name:
            return name[0]

    def get_image_src(self , content_id):
        cursor = sqlite3.connect(self.root_dir).cursor()
        name = cursor.execute(f"SELECT image_src FROM SHORT_TABLE WHERE id = {content_id}").fetchone()
        if name:
            return name[0]


    def get_series_name(self , series_name , parent= False):
        NAME = self.clean_name(series_name)
        cursor = sqlite3.connect(self.root_dir).cursor()
        if not str(series_name).isdigit() :
            query = f"SELECT series_name FROM SERIES WHERE item_name = '{series_name}'"
        else:
          query =  f"SELECT series_name FROM SERIES WHERE content_id = {series_name}"
        name = cursor.execute(query).fetchone()
        if name :
            return  name[0]
        else:
            None


    def get_full_series(self , series_name):
        cursor = sqlite3.connect(self.root_dir).cursor()
        query = f"SELECT item_name FROM SERIES WHERE series_name = '{series_name}'"
        series_ids = cursor.execute(query).fetchall()

        SERIES_IDS3= []
        for i in series_ids:
            if i not in SERIES_IDS3:
                if len(i) > 1:
                    i = i[0]
                SERIES_IDS3.append(i)

        series_list =[]
        if series_ids:
            for i in SERIES_IDS3:
                result = self.get_series(NAME=i , all=True)
                series_list.append(result[0])
            # print("hete are se;cted ids",series_list)
            return series_list
        else:
            print("found no series coeesponfinh to that name")
            return None


    def get_stream_data(self , name=None):
        """
        return ([MOVIES = (content_id , name , image_src)] ,[SERIES = (content_id , name , series_name,image_src)] )
        """
        if name != None:
            content_id = self.get_content_id(name=name)
            content_path = self.get_full_path(content_id=content_id)
            if "SERIES" in content_path:
                return self.get_series(name , all=True)
            elif "MOVIES" in content_path:
                return self.get_movies(name , all=True)
            else:
                raise ValueError("UN ECPECTED REQUEST" , name , content_path)


        movies = self.get_movies(NAME="MOVIES" , all=True)
        series = self.get_series(NAME = "SERIES" , all=True)

        streaming_content = [[] , []]
        for movie_data in movies:
            content_id , item_name , image_src = movie_data
            if self.determine_if_downloadable(content_id=content_id):
                pass
            else:
                if   (image_src != None and image_src != "None"):
                    streaming_content[0].append((content_id , item_name , image_src))

        for series_data in series:
            content_id , item_name ,image_src = series_data
            # print("here is eslf  f" ,item_name ,self.determine_if_downloadable(content_id=content_id))
            if self.determine_if_downloadable(content_id=content_id):
                pass
            else:
                if   image_src != None and image_src != "None":
                    streaming_content[1].append((content_id , item_name ,image_src))

        return streaming_content


    def get_distinc_series(self , downloadable = False):
        cursor = sqlite3.connect(self.root_dir)
        query = f"SELECT  series_name FROM SERIES"
        series_names = cursor.execute(query)
        res =[]
        for i in series_names:
            i =i[0]
            if i not in res:
                res.append(i)

        final_res =[]
        for name in res:
            query = f"SELECT content_id, image_src FROM SERIES WHERE series_name = '{name}'"
            data  = cursor.execute(query).fetchone()
            if data:
                series_id =data[0]
                image_src = data[1]
                if image_src != None and image_src != "None":
                    if self.determine_if_downloadable(series_id) == downloadable:
                        final_res.append((series_id , name , image_src))

        return final_res



    def grab_universally(self , name):
        db =sqlite3.connect(self.root_dir)
        cursor = db.cursor()

        if str(name).isdigit():
            content_id = [str(name)]
            name = self.get_content_name(content_id=content_id[0])
        else:
            content_id = cursor.execute(f"SELECT id FROM SHORT_TABLE WHERE item_name = '{name}'").fetchone()

        if content_id:
            content_type = self.get_content_type(content_id=content_id[0])
        else:
            content_type = name
        print("HEre os content type" , content_type)
        if content_type == "SERIES":
            return self.get_series(name)

        if content_type == "MOVIES":
            return self.get_movies(name)

        if content_type == "GAMES":
            return self.get_game(name)
        if content_type == "STREAM":
            if name != content_type:
                return self.get_stream_data(name=name)
            # print("here is name" , name)
            return self.get_stream_data()
        return self.get_game(name)

    def __getitem__(self , name):
        if isinstance(name ,(list , tuple)):
            return list(map(self.grab_universally , name))
        return self.grab_universally(name)

from config import CONTENT_LOCATION , DATABASE_LOCATION , USER_DB_LOCATION

if __name__ == "__main__":
    database_path = CONTENT_LOCATION
    database = DatabaseManager(data_base_path=database_path)

    database.format_images()
    database.generate_db_jsons()
    database.update_db_file()

    # db_connection = sqlite3.connect(DATABASE_LOCATION)
    # # clean_db(db_connection=db_connection)

    # view_all_tables_and_content(DATABASE_LOCATION)
    db = DataBaseIndex(DATABASE_LOCATION)
    print(db[1])













