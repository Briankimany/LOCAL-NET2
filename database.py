
from pathlib import Path
from PIL import Image
from utils import save_load_program_data
import os
import sqlite3
from pathlib import Path

from databaseutils import prepare_data_base_jsons ,create_database, update_db 
from config import DATA_BASE_FILE_TYPES , DISPLAY_NO_IMAGE_CONTENT

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


        self.data_base_file_types = DATA_BASE_FILE_TYPES
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
                try:
                    image  = Image.open(image_path)
                    image = image.resize(size=size)
                    image.save(fp = image_path)
                except Exception as e:
                    print(str(e))
                    pass


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
       
            path = Path(path)
            if path.exists():
                continue
            else:
                path.mkdir(parents=True)

        for name ,folder in data_base_design.items():
            folder = Path(folder)
            if "MOVIES" in str(folder) or "SERIES" in str(folder):

                file_types = DATA_BASE_FILE_TYPES[0]
            elif "GAMES" in str(folder):
                file_types =DATA_BASE_FILE_TYPES[1]
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






















