import tempfile
from datetime import timedelta
import requests , random , time
from tqdm.auto import tqdm
import string
from datetime import datetime, timedelta
from pathlib import Path
import  shutil
import json
import pickle
import time





def log_str(file_path: Path , message , mode = 'a'):
    with open(file_path , mode) as file:
        file.write(message)


def get_time(string_obj  = True):
    current_time = time.localtime()
    if not string_obj:
        return current_time
    formated_time = time.strftime("%Y/%b/%d  %H:%M:%S" , current_time)
    return formated_time

def save_pickle_dict(path , data={} , mode = 'rb'):
    with open(path ,mode) as file:
        if mode =='rb':
            file_info = pickle.load(file)
            return file_info
        elif mode == 'wb':
            pickle.dump(data , file=file)
            return data




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

    try:
     
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
        # os.rename(temp_file.name, path)
        shutil.move(temp_file.name , path)
        # print(f"moved {temp_file.name} to {path}")
    except Exception as e:
        print(f"Error saving/loading data: {e}")
        return None



def save_load_program_data(path , data=None , mode ='r'):
    try:    
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
    except KeyboardInterrupt:
        # print("Key board interupt but saving data before writing it " , data_before_error)
        pass
    except Exception as e:
        print(e)

def log_error(error , path):
    name = type(error).__name__ +".json"
    file_path = Path(path)/"ERRORS"/name 
    file_path.parent.mkdir(parents = True , exist_ok = True)
    save_load_program_data(path=file_path , mode='w' , data= {f"ERROR {get_time()}":str(error)})


def get_link_default_state():
    default_state = {'parent_dir': Path('Movies'),
                    'log_dir': Path('LOGS'),
                    'url': None,
                    'extension': None,
                    'final_link':None,
                    'file_size': None,
                    'full_path': None,
                    'length': None,
                    'is_downloaded': False,
                    'in_data_base': True,
                    'chunk_size': 1024,
                    'name': None,
                    'short_name': None,
                    'remaining_size': None,
                    'hard_drive_file_size': 0,
                    'remainig_size_percentage': 1.0}
    return default_state



def get_file_size(link):
    try:
        if link.final_link == None:
            # print(link.url , link.name)
            response = requests.head(link.url)
            max_count =0
            redirect_link = link.url
            while int(response.status_code) == 302:
                # time.sleep(1.5)
                # print(response.status_code , link)
                redirect_link = response.headers['Location']
                response = requests.head(redirect_link)
                max_count+=1
                if max_count == 10:
                    return None , None
            if "File-Size" in response.headers:
                file_size = int( response.headers["File-Size"]) / 1024**2
            else:
                file_size = int(response.headers.get('content-length', 0)) / 1024**2
        else:
            redirect_link = link.final_link
            file_size= link.file_size
        
        return file_size , redirect_link
    except Exception as e:
        link.log(message=str(e))
        return None , None
        
        
def convert_duration_format(duration_str):
    # Parse the duration string
    try:
        hours = 0
        minutes =0
        seconds = 0
        # Extract hours, minutes, and seconds from the duration string
        if 'H' in duration_str:
            hours = int(duration_str.split('H')[0][1:])
        if 'M' in duration_str:
            minutes = int(duration_str.split('M')[0][-2:])
        if 'S' in duration_str:
            seconds = int(duration_str.split('S')[0][-2:])

        # Construct a timedelta object
        duration_timedelta = timedelta(hours=hours, minutes=minutes, seconds=seconds)
        
        return duration_timedelta
    except Exception as e:
        print(str(e))
        return None

    

def change_str_deltatime(time_delta_str):
    time_delta = datetime.strptime(time_delta_str, '%H:%M:%S')
    time_delta = timedelta(hours=time_delta.hour, minutes=time_delta.minute, seconds=time_delta.second)
    return time_delta
        

def generate_random_chars(k):
    random_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=k))
    return random_chars



def save_load_logs(data , mode , path):
    # Open a file in write mode
    with open(path, mode) as file:
        # Iterate through each key-value pair in the JSON object
        for key, value in data.items():
            # Convert key-value pair to JSON string
            json_str = json.dumps({key: str(value)})
            # Write JSON string to file followed by a newline character
            file.write(json_str + "\n")



def merge_class_data_base_dict(dict1 ,dict2):
    """
    Input = {link :{....}
            }
    """
    if isinstance(dict1 , Path):
        dict1 = save_load_program_data(path = dict1)
        dict2 = save_load_program_data(path=dict2)
        
    max_dict = dict1
    min_dict = dict2
    
    if len(list(dict2.keys())) > len(list(dict1.keys())) :
        max_dict = dict2
        min_dict = dict1
        
    result_dict = max_dict.copy()
    for key in min_dict:
        if key in result_dict:
            pass
        else:
            result_dict[key] = min_dict[key]
    print(len(list(dict1.keys())) , len(list(dict2.keys())) , len(list(result_dict.keys())))
    return result_dict    


def log(link , mesage , class_ = 'e' , path_ ="Logs" ):
        if class_ == 'e':
            info = str(mesage)
        else:
            info= str(mesage)
            
        if link.full_path.parent.is_dir():
            path_ = link.full_path.parent /path_
        logger_dir = Path(path_)
        logger_dir.mkdir(exist_ok=True , parents=True)
        error_path = logger_dir/link.short_name
        error_path = error_path.with_suffix('.json')
        logs = link.get_state().update({"Error":info})
        save_load_program_data(path=error_path , data=logs , mode='w')



     

if __name__ == "__main__":
    pass