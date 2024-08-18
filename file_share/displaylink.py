

from urllib.parse import urlsplit , urljoin
from pathlib import Path
class Displaylink:
    def __init__(self ,link , name , is_file= False , parent_link = None) -> None:
        self.link = link
        self.name = name
        self.is_file = is_file
        self.parent_link = parent_link

        # print(self.__dict__)
    def display(self):
        return self.name
    def step_back(self):
        link = urlsplit(self.parent_link)
        link_host= link.netloc
       
        link_parts = Path(link.path)

        new_path = link_parts.parent

        new_link = link.scheme + "://"+ link_host + str(new_path.as_posix())
        self.link  =  self.parent_link
        self.parent_link = new_link
        
        
        # print(f"currently viewing {self.link} Took a tep back from" ,self.link , "--->",self.parent_link)