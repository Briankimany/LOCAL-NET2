import sqlite3
from pathlib import Path
import sqlite3
from pathlib import Path
import random

from config import CONTENT_LOCATION 
from utils import get_time , save_load_program_data
from config import   DISPLAY_NO_IMAGE_CONTENT

from PIL import Image



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
                if not DISPLAY_NO_IMAGE_CONTENT:
                    image_needed = (image_src != None and image_src != "None")
                else:
                    image_needed = True
                    
                if self.determine_if_downloadable(movie_id) and image_needed:
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
            series = list(cursor.execute("SELECT content_id , item_name , image_src FROM SERIES WHERE item_name = ?" , (NAME,)).fetchall())
        else:
            series_query = f"SELECT content_id , item_name ,image_src FROM SERIES"
            series = list(cursor.execute(series_query).fetchall())

        if all:
            series_copy= series
        else:
            series_copy = []
            for i in series:
                series_id , item_name ,image_src =i
                        
                if not DISPLAY_NO_IMAGE_CONTENT:
                    image_needed = (image_src != None and image_src != "None")
                else:
                    image_needed = True
                if self.determine_if_downloadable(series_id) and image_needed:
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

    
    def grab_common_image(self):
        common_images_dir = CONTENT_LOCATION /"PROFILE_PICS" / "COMMON"
        
        if common_images_dir.exists():
            images_list = list(common_images_dir.glob("*.jpg"))
            
            if len(images_list) > 1:
                image_path = random.choice(images_list)
            elif len(images_list) == 1:
                image_path = images_list[0]
            elif len(images_list) == 0:
                return None
            return image_path
        else:
            common_images_dir.mkdir(exist_ok = True , parents = True)
            return None

    def get_image_src(self , content_id):
        cursor = sqlite3.connect(self.root_dir).cursor()
        name = cursor.execute(f"SELECT image_src FROM SHORT_TABLE WHERE id = {content_id}").fetchone()
        if name[0]:
            return name[0]
        else:
            if DISPLAY_NO_IMAGE_CONTENT:
                return self.grab_common_image()

    def get_series_name(self , series_name , parent= False):
        NAME = self.clean_name(series_name)
        cursor = sqlite3.connect(self.root_dir).cursor()
        if not str(series_name).isdigit() :
            # query = f"SELECT series_name FROM SERIES WHERE item_name = '{series_name}'"
            name = cursor.execute("SELECT series_name FROM SERIES WHERE item_name =? " , (series_name,)).fetchone()
        else:
        #   query =  f"SELECT series_name FROM SERIES WHERE content_id = {series_name}"
          name = cursor.execute("SELECT series_name FROM SERIES WHERE content_id =? " , (series_name,)).fetchone()
        if name :
            return  name[0]
        else:
            None


    def get_full_series(self , series_name):
        cursor = sqlite3.connect(self.root_dir).cursor()
        query = f"SELECT item_name FROM SERIES WHERE series_name = '{series_name}'"
        series_ids = cursor.execute(query).fetchall()

        SERIES_IDS3= []
        for i in sorted(series_ids):
            if i not in SERIES_IDS3:
                if len(i) > 1:
                    i = i[0]
                SERIES_IDS3.append(i)

        series_list =[]
        if series_ids:
            for i in SERIES_IDS3:
                result = self.get_series(NAME=i , all=True)
                series_list.append(result[0])

            return series_list
        else:
            print("found no series corresponding to that name")
            return None

    def get_random_series_id(self , series_name):
        "Returns a random series episode id"
        series_ids = self.get_full_series(series_name=series_name)
        if series_ids:
            return series_ids[0][0]


    def is_movie(self , content_id):
            content_path = self.get_full_path(content_id=content_id)
            if "MOVIES" in content_path:
                return True
            return False

   
    
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
                raise ValueError("UN EXPECTED REQUEST" , name , content_path)


        movies = self.get_movies(NAME="MOVIES" , all=True)
        series = self.get_series(NAME = "SERIES" , all=True)

        streaming_content = [[] , []]
        for movie_data in movies:
            content_id , item_name , image_src = movie_data
            if self.determine_if_downloadable(content_id=content_id):
                pass
            else:
                if not DISPLAY_NO_IMAGE_CONTENT:
                    image_needed = (image_src != None and image_src != "None")
                else:
                    image_needed = True
                if   image_needed:
                    streaming_content[0].append((content_id , item_name , image_src))

        for series_data in series:
            content_id , item_name ,image_src = series_data
            # print("here is eslf  f" ,item_name ,self.determine_if_downloadable(content_id=content_id))
            
            if self.determine_if_downloadable(content_id=content_id):
                pass
            else:
                if not DISPLAY_NO_IMAGE_CONTENT:
                    image_needed = (image_src != None and image_src != "None")
                else:
                    image_needed = True
                if   image_needed:
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
                if not DISPLAY_NO_IMAGE_CONTENT:
                    image_needed = (image_src != None and image_src != "None")
                else:
                    image_needed = True
                if image_needed:
                    if self.determine_if_downloadable(series_id) == downloadable:
                        final_res.append((series_id , name , image_src))

        return final_res
    
    def get_check_out_image(self , content_id , size = (100 , 100)):
        image_path = self.get_image_src(content_id=content_id)
        image = Image.open(image_path)
        image = image.resize(size)
        return image

    def grab_no_profiles(self):
        db = sqlite3.connect(self.root_dir)
        cursor = db.cursor()
        query = "SELECT content_id, item_name FROM NO_PROFILES"
        data =cursor.execute(query).fetchall()
        final_data =[]
        no_profile = {}
        for content_id  , content_name in data:
            content_type = self.get_content_type(content_id)
            content_path = self.get_full_path(content_id)

            if content_type == "SERIES" or  'SERIES' in str(content_path):
                content_name = self.get_series_name(content_name)
                full_series = [self.get_full_path(i[0]) for i in self.get_full_series(content_name)]
                
                no_profile[content_name] = full_series , content_type
            else:
                no_profile[content_name] = [self.get_full_path(content_id) , content_type]
            
        return  no_profile


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
        # return self.get_game(name)

    def __getitem__(self , name):
        if isinstance(name ,(list , tuple)):
            return list(map(self.grab_universally , name))
        return self.grab_universally(name)