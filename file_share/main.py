
import sys
try:
    import requests
    from bs4 import BeautifulSoup as soup
    from pathlib import Path
    from urllib.parse import urlparse
    
    import concurrent
    from concurrent.futures import ThreadPoolExecutor

    from format_link import  FormatLink
    from config import AUTOMATED ,SKIP_DIRS
    from displaylink import Displaylink 

    import os 
    import posixpath  , ntpath
    import re
    from master import save_load_program_data , save_pickle_dict , log_str , get_time
except Exception as e:
    with open("logs.txt" , 'w') as file:
        file.write(str(e))
    sys.exit()

def make_request(link , time_out =10):
    log_ = False
    if (isinstance (link , FormatLink)):
        link_url = link.url
        log_ = True
    elif not isinstance (link , FormatLink):
        link_url = link
    
    try:
        # print("making requests" , link_url)
        requested_info= requests.get(link_url , timeout=time_out)
        
        parsed_data = soup(requested_info.content , features= "lxml")
        parsed_data.from_link = link_url
        link_p = urlparse(link_url)
        host_link = link_p.scheme + "://"+ link_p.netloc
        parsed_data.host_link = host_link
        # print(requested_info.status_code)
        
        if int(requested_info.status_code) == 404:
            if log_:
                link.log(str(requested_info.status_code))
            print("404 ERROR ")
            return "404 ERROR " , "404 ERROR "

        return requested_info.status_code , parsed_data
    except TimeoutError as e:
        if log_:
            link.log(str(e))
        print("Timed out")
        return "TIME OUT" , "TIME OUT"
    except Exception as e:
        print(f"Error while fetching data from: {link_url} , {e}")
        if log_:
            link.log(str(e))
        return None , None

def get_data(link=None):
    """Get user input for link, name, and destination"""
    # print("gettinf data for this final link link" , link)
    if link == None:
        link = input("Paste the link: ").strip("\"")
    fileheaders = requests.head(link).headers
    if "File-name" in fileheaders:
            name = fileheaders['File-name']
            if os.name == 'posix':
                name = str(name).replace(ntpath.sep , posixpath.sep)
                print("here is the new name" , name)
            final_name = Path(name).name
            destination = Path(name).parent  
            message = get_time() + f"\t NAME :{final_name}\t\t\t\destination: {destination}\n"
           
            log_str(file_path=Path("get_data_function_logs.txt") , message=message)
            if destination != "":   
                    pass
            else:
                if AUTOMATED:
                    return None ,None ,None
                destination = input("Destination: ") or "DOWNLOADS"  # default destination if empty
            # print(f"using default name final name {final_name} , final destination {destination}")
    else:
        if AUTOMATED:
            return None ,None ,None
        name = input("Name: ") or "content"  # default name if empty
        destination = input("Destination: ") or "DOWNLOADS"  # default destination if empty
    return link, final_name, destination

def savefile(link = None): 
    link, name, destination = get_data(link=link)
    message = get_time() + f"\tLINK: {str(link)}\t\t\tNAME: {str(name)}\t\t\DESTINATION: {str(destination)}\n"
    print("here is out from get data" , message)
    log_str(file_path="save_file_function_logs.txt" , message=message )
    if link == None:
        print("Got None " , link , name , destination)
        return None
    formated_link = FormatLink(link_data=(link, name), parent_dir=destination , chunk_size=1024 , in_data_base=True , is_verified_final_link=True)
   
    if not AUTOMATED:
        formated_link.inspect()
    if formated_link.file_size == 0:
        formated_link.log(message="got filse size as zero")
        return None
    return formated_link.start_download()
    

def get_folders(link):
    # print("geting folders for this link", link)
    status_code , data = make_request(link)
    if status_code == 200:
        roots = data.find_all("a")
        dirs =[]
        files =[]
        for i in roots:
            l = data.host_link +i['href']  , i.text
            name =  i.text
            if name.endswith(".file"):
                files.append(l)
            else:
                dirs.append(l)
        return list(sorted(dirs)) , list(sorted(files))
    else:
        F = "errors_logs.json"
        if Path(F).exists():
            d = save_load_program_data(F)
        else:
            d ={}
        d.update({link:status_code})
        save_load_program_data(path=F , data= d , mode='w')
        return [] ,[]
    
    
def save_current_files(files):
    with ThreadPoolExecutor() as executor:
        results = [executor.submit(savefile , file[0]) for file in files]
    for result in concurrent.futures.as_completed(results):
        result.result()

def recurse_folder(folder_link):
    print("Recursing on" , folder_link)
    dirs  , files= get_folders(folder_link)
    # print("\n\nHEre are the found files and folders " , files , dirs)
    save_current_files(files=files)
    
    for folder in dirs:
        # print(folder)
        recurse_folder(folder_link=folder[0])
   
def autorun(link = None):

    done = []
    if link == None:
        link = input("Enter server link: ") or "http://10.42.0.140:5000/"
    dirs  , files= get_folders(link)

    if len(files) > 0:
        print(f"\nSaving {len(files)} files in root folder ...\n")
        save_current_files(files=files)
    
    for folder in dirs:
        # print(f"Moving next to: {folder[1]}\n\n")
        if folder[0] not in done:
            recurse_folder(folder_link=folder[0])
            done.append(folder[0])
        dirs , files = get_folders(link=link)

def singlerun(link = None):
    link, name, destination = get_data(link=link)
    if link == None:
        pass
    formated_link = FormatLink(link_data=(link, name), parent_dir=destination , chunk_size=1024 , in_data_base=False)
    
    if not AUTOMATED:
        formated_link.inspect()

    if formated_link.file_size == 0:
        # print("\n\n\nGot this file size as zero\n",formated_link.__dict__ , "\n\n\n")
        formated_link.log(message="file size is zero")
        return None
    formated_link.start_download()


def start_download(link):
    if link == None:
        return None
    if link.is_file:
        savefile(link = link.link)
    else:
        autorun(link=link.link)


def view_files_fiolders(files , folders , parent_link = None):
        final_dict = {}
        display_files = dict([(i+1 , Displaylink(link = files[i][0] , name =files[i][1] , is_file = True , parent_link=parent_link) ) for i in  range(len(files))])
        display_folders =  dict([(i+1+len(files),  Displaylink(link = folders[i][0] , name = folders[i][1] , parent_link=parent_link) ) for i in range(len(folders))])

        
        files_string = "\n".join([f"{i}: {display_files[i].display()}" for i in display_files])
        folder_strings =  "\n".join([f"{i} : {display_folders[i].display()}" for i in display_folders])

        print("FILES\n")
        print(files_string)
        print("\n")
        print("FOLDERS\n")
        print(folder_strings)

        final_dict = display_files.copy()
        final_dict.update(display_folders)

        return final_dict



def multirun():
    while True:
        try:
            server_link = input("Enter host link: ")
            server_link = Displaylink(link=server_link ,name = "ROOT",parent_link=server_link)
            folders , files = get_folders(server_link.link)
            break
        except Exception as e:
            print(f"Got Error (str(e))")

    final_dict = view_files_fiolders(files=files , folders=folders ,parent_link=server_link.link)
    link = server_link
    while True:
        choice = input("Choose: index element to change into it and (D:<1,2,3,4>) to download: ") or None

        if choice != None and  "D:" in choice:

            files_index = (choice.replace("D:" , '')).split(",")
            files_index = [int(file_index) for file_index in files_index]
            links = list(map(final_dict.get , files_index))
            # print("Here are the file links" , links , files_index , choice)
            def procces1(link=links):
                # print("DOwnloading this link" , links[0].link)
                for link in links:
                    start_download(link)
            procces1(link=links)

        elif choice != None and "B" in choice :
            break

        else:
            if choice == None:
                    pass
            else:
                choice = int(re.sub("\D" , "" , choice)) 
                if choice in final_dict:
                    link = final_dict.get(int(choice))

            if choice: 
                if link.is_file:
                    start_download(link=link)
                    # print(f"Made a request for this file {link.link} and now making a request to this {link.parent_link}" )
                    folders , files = get_folders(link=link.parent_link)
                else:
                    folders , files = get_folders(link=link.link)

            else:
                # print(f"Here is link before step back {link.link}")
                link.step_back()
                folders , files = get_folders(link=link.link)
                
        # print(f"\nThese foldres and files are for {link.link} whose oarent link is {link.parent_link}\n")
        final_dict = view_files_fiolders(files=files , folders=folders , parent_link=link.link)


def cleint_tool():
    file = Path("data.bin")
    if file.exists():
        info = save_pickle_dict(file)
        link = info['LINK']
        autorun(link = link)
    else:
        print("No file data found !!")
    
if __name__ == "__main__":
    # multirun()
    save_pickle_dict("data.bin" , {"LINK":"http://192.168.184.239:5000/TORRENT/QBIT/COMPLETE/game%201"} , 'wb')
    # cleint_tool()
    multirun()