from pathlib import Path
from master import save_load_program_data 
import os
local_share_conf_path = Path("local_share.conf")
if local_share_conf_path.exists() and local_share_conf_path.is_file():
    confs = save_load_program_data(local_share_conf_path)

else:

    if os.name =='posix':
        current_dir =Path( os.getcwd())
        current_dir.home
        default_folder = "/home"
        relative_dir = "/home"
    if os.name == 'nt':
        default_folder = Path(os.getcwd()).drive
        relative_dir = input("Enter folder disk:  ") or  Path(os.getcwd()).home()

    serve_folder = input("Which folder to share: ") or default_folder 
    automated = input("Automate download?:(Y,N): ") or True
    if automated == True:
        pass
    elif str(automated.upper()) == 'Y':
        automated = True
        
    elif str(automated.upper()) == 'N':
        automated = False
    
    confs = {"AUTOMATED": automated,'DEFAULT DIR':str(default_folder) ,'RELATIVE DIR':str(relative_dir), 'SHARING FOLDER':str(serve_folder) }
    save_load_program_data(path=local_share_conf_path , data=confs , mode='w')

automated = confs['AUTOMATED']
default_folder = confs['DEFAULT DIR']
relative_dir = confs['RELATIVE DIR']
serve_folder = confs['SHARING FOLDER']


SKIP_DIRS =['__pycache__' , 'flask' , 'win_flask']
SERVE_FOLDER = serve_folder
AUTOMATED = automated
RELATIVE_DIR = relative_dir
DEFAULT_DIR = default_folder