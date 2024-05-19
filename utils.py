
import tempfile , json
from pathlib import Path
import os , shutil
import time


def get_time(string_obj  = True):
    current_time = time.localtime()

    if not string_obj:
        return current_time
    formated_time = time.strftime("%Y/%b/%d  %H:%M:%S" , current_time)
    return formated_time

def get_max_dict(dict1 , dict2):
    max_d = dict1
    min_d = dict2

    if len(list(dict1.items()))< len(list(dict2.items())):
        max_d = dict2
        min_d = dict1
        return False

    return  True


def convert_dict(dict1 , to_string = False):
    temp = {}
    for key , value in dict1.items():
        if not to_string:
            temp[Path(key)] = Path(value)
        else:
            if value == None:
                temp[str(key)]= value
            else:
                temp[str(key)]= str(value)
    return temp


def prepare_data_for_full_dict(dict1):
    temp = {}
    for key , val in dict1.items():
        temp[Path(key.name)] = Path(key.parent)
    return  temp




def save_program_data(path, data, mode='w'):
    """
    Saves or loads data to/from a JSON file.

    Args:
        path (str): The path to the JSON file.
        data (dict, optional): The data to be saved to the file. Defaults to None.
        mode (str, optional): The mode to open the file in. Can be either 'r' for reading or 'w' for writing. Defaults to 'r'.

    Returns:
        dict or None: The loaded data or None if an error occurred.
    """

    # try:
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        if mode == 'w':
            for key, value in data.items():
                json_str = (json.dumps({key: value})+ "\n").encode('utf-8')
                temp_file.write(json_str )
        elif mode == 'r':
            full_data = {}
            for line in temp_file:
                loaded_json = json.loads(line)
                full_data.update(loaded_json)
            return full_data
        temp_file.flush()
    real_path = os.path.realpath(path)
    shutil.move(temp_file.name, real_path)
    # print(f"renaimg this {path} and {")
    # os.rename(temp_file.name, os.path.realpath(path))
    # except Exception as e:
    #     print(f"Error saving/loading data: {e}")
    #     return None



def save_load_program_data(path , data=None , mode ='r'):
    # try:
        if mode =='r':
            with open(path, 'r') as file:
                full_data = {}
                for line in file:
                    # try:
                        loaded_json = json.loads(line)
                        full_data.update(loaded_json)
                    # except json.JSONDecodeError:
                        # print("Error decoding JSON:", line)
                        # return {}
                # print("loded data", list(full_data.items()), path)
                return full_data
        elif mode =='w':
            save_program_data(path=path , data= data)
    # except KeyboardInterrupt:
    #     # print("Key board interupt but saving data before writing it " , data_before_error)
    #     pass
    # except Exception as e:
    #     print(e)


def compare(ruler , follow):
    # print(f"here is ruler{len(ruler)} \n here is fololoer{len(follow)}\n")
    result_dict = {}
    for item in ruler:
        found_profile = False
        key = item
        for item2 in follow:
            if Path(item2).suffix in ['.jpg' ,'.png' , '.jpeg' , '.webp']:
                key = item
                value_ = item2
            else:
                key = item2
                value_ = item
            # print("comparing" , key , value_)
            if key.stem == value_.stem:
                result_dict[Path(key)] = Path(value_)
                found_profile = True
                break
        if not found_profile:
            # print("found no patner")
            if Path(key).is_symlink():
                key = os.path.realpath(key)
            result_dict[key] = None

        # print("\n")
    return result_dict


def get_dir_content(directory , file_types = [".mp4"] , debuging = False , get_intermideary = False) -> Path:
    source_dir = directory if isinstance(directory , Path) else Path(directory)
    movies_profile = list(source_dir.glob("*.png")) + list(source_dir.glob("*.jpg")) + list(source_dir.glob("*.jpeg"))

    directories = os.listdir(source_dir)

    for m in movies_profile:
        m = Path(m).with_suffix(".jpg")
    movies_files =[]
    for file_type in file_types:
        data = source_dir.glob(f"*{file_type}")
        movies_files.extend(data)

    ruler = movies_files
    follow = movies_profile

    if len (movies_profile) >  len(movies_files):
        ruler = movies_profile
        follow = movies_files

    elif len(movies_files) == len(movies_profile):
        pass

    result_dict = {}

    if len(movies_files) == 0:
        follow =[(Path(i).with_suffix(".zip")).absolute() for i in ruler]
        movies_files = [(Path(i).with_suffix(".zip")).absolute() for i in movies_profile]

    for item in movies_files:
        print(item)
        for item2 in movies_profile:
            if Path(item2).suffix in ['.jpg' ,'.png' , '.jpeg']:
                key = item2
                value_ = item
            else:
                key = item
                value_ = item2

            if key.stem == value_.stem:
                result_dict[Path(item)] = Path(item2)
                break


    dict_path = source_dir / "tracker.json"
    # print("here is teh result dict" , result_dict)

    if debuging:
        debuging_name = f"test.json"
        save_load_program_data(path=(source_dir/debuging_name) , data= convert_dict(result_dict.copy() , to_string=True) , mode='w')
    if dict_path.is_file():
        present_dict = save_load_program_data(path=dict_path)
        present_dict = convert_dict(present_dict)

        if get_max_dict(present_dict , result_dict):
            present_dict.update(result_dict)
            final_d = present_dict
        else:
            result_dict.update(present_dict)
            final_d = result_dict

    else:
        final_d = result_dict

    save_load_program_data(path=dict_path , data = convert_dict(final_d ,to_string=True) , mode = "w")
    return dict_path






if __name__ =="__main__":
    directory = "/home/Kimany/playpit/content2/GAMES"
    path = get_dir_content(directory , file_types = [".zip"] , debuging = True , get_intermideary = False)











