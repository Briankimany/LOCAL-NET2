from flask import Flask,request , make_response , current_app 
import os  , re
from pathlib import Path
from config import SERVE_FOLDER , RELATIVE_DIR , SKIP_DIRS

app = Flask(__name__)

def get_chunk(file_path, start, chunk_size):
    with open(file_path, "rb") as f:
        f.seek(start)
        chunk = f.read(chunk_size)
    return chunk


def send_file_mine(filename):
    
    filename = Path(filename)
    if not filename.is_file():
        raise FileNotFoundError(f"File not found: {filename}")

    content_path = filename
    headers = request.headers
    file_type = filename.suffix
    file_size = os.path.getsize(content_path)

    if "Chunk-size" in headers:
        chunk_size = int(re.sub("\D", "", headers["Chunk-size"]))
    else:
        chunk_size = (10 **6) * 30
    if "Range" not in headers:
        file_size = os.path.getsize(content_path)
        start = 0
        end = min(chunk_size- 1, file_size - 1)
        content_length = end - start + 1

        with open(content_path, "rb") as f:
            f.seek(start)
            content_chunk = f.read(content_length)

        response = make_response(content_chunk, 206)
        response.headers["Content-Type"] = file_type
        response.headers["Content-Range"] = f"bytes {start}-{end}/{file_size}"
        response.headers["Accept-Ranges"] = "bytes"
        response.headers["content-length"] = str(file_size)
        response.headers["File-name"] = filename.relative_to(RELATIVE_DIR)
        response.headers["File-Size"] = str(file_size)
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        
        data = get_chunk(filename ,start ,chunk_size )
        return current_app.response_class(data, headers=response.headers,status=200)
    
    else:
       
        size = os.stat(content_path).st_size
        start = int(re.sub("\D", "", headers["Range"]))
        
        if start > size:
            return current_app.response_class(status=416)
        
        end = min(start + chunk_size, size - 1)
        content_length = end - start + 1
        print("Hrese is where to start" , request.headers['Range'] ,"Here is the start" , start , end , content_length) 
        response_headers = {
            "Content-Range": f"bytes {start}-{end}/{size}",
            "Accept-Ranges": "bytes",
            "content-length": file_size,
            "Content-Type": file_type,
            "File-Size":str(file_size),
            "File-name": filename.relative_to(RELATIVE_DIR),
        }
        
        response = make_response(b"", 206 ,)
        response.headers.update(response_headers)


        return current_app.response_class(get_chunk(content_path, start, chunk_size), headers=response.headers , status=206)



def serve_file(file_path):
    return send_file_mine(file_path)

def serve_directory(path):
    # print(request.path)
    # return '<br>'.join(['<a href="' + os.path.join(request.path, file) + '">' + file + '</a>' for file in os.listdir(path)])
    page =[]
    for file in os.listdir(path=path):
        if  Path(os.path.join(path, file)).is_file():
            extra = ".file"
        else:
            extra=""
        html_line = '<a href="' + os.path.join(request.path, file) + '">' + file  + extra + '</a>'
        page.append(html_line)
        
    return "<br>".join(page)
        

@app.route('/')
def list_torrent_dir():
    return serve_directory(SERVE_FOLDER)

@app.route('/<path:path>')
def serve_path(path):
    full_path = os.path.join(SERVE_FOLDER, path)
    if os.path.isfile(full_path):
        return serve_file(full_path)
    elif os.path.isdir(full_path) and Path(full_path).name not in SKIP_DIRS:
        return serve_directory(full_path)
    else:
        return "Path not found", 404

if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True)