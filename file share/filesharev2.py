# import main
from pathlib import Path
from master import save_pickle_dict
import sys
from main import autorun 
from master import log_error 
import os , requests

file_path = Path("data.bin")

save_pickle_dict(path = file_path ,data={"LINK":"http://127.0.0.1:5000/brian/TORRENT"} ,mode ='wb')


if file_path.exists() and file_path.is_file():
    file_info = save_pickle_dict(path=file_path)
else:
    print("NO conf data found !!!!")
    sys.exit()

# try:
link = file_info['LINK']
print(link)
g = requests.get(link)
print(g.content)
# autorun(link=link)
# except Exception as e:
#     log_error(error=e , path=os.getcwd())

    



