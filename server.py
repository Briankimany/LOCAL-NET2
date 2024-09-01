
from flask import Flask
from flask import  redirect, url_for , render_template , send_from_directory , make_response , request  , current_app , send_file , session  , Response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import Flask, request, jsonify
from flask_httpauth import HTTPTokenAuth




import re
import os
import time
from pathlib import Path
from functools import wraps

from database_index import DataBaseIndex
from users import Users 
from users_data import UniqueUser
import logging
from config import CONTENT_LOCATION , DATABASE_LOCATION , USER_DB_LOCATION , UPLOAD_DIR
from pathlib import Path
from file_share.master import log_str , save_load_program_data , get_time
from urllib.parse import urlparse


from urllib.parse import urlencode, urlunparse


app = Flask(__name__)
auth = HTTPTokenAuth(scheme='Bearer')

app.config['STATIC_FOLDER'] = os.path.abspath('templates/static')
app.secret_key='KIMANI'

download_limiter = Limiter(
    get_remote_address,
    app=app,

)

users_db = Users(CONTENT_LOCATION)
db_indexer = DataBaseIndex(db_path=DATABASE_LOCATION)

# In a real application, you would store these tokens securely, perhaps in a database
TOKENS = {
    "123456789": "ajay",
    "987654321": "patrick",
}

app.logger.setLevel(logging.DEBUG)  # Set the logging level (DEBUG, INFO, etc.)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = logging.StreamHandler()  # Log to console
handler.setFormatter(formatter)
app.logger.addHandler(handler)




def set_current_url(scheme, server_addres , path='' , query_params= {},fragment=""  ,set_url = True):
    encoded_params = urlencode(query_params)
    url = urlunparse((scheme ,server_addres , path , '', encoded_params, fragment ))
    if  set_url:
        session['current_url'] = url
    return url


def login_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        # print("calling the decorated funtion")
        if 'user' not in session:
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return decorated_function



@app.route("/" ,  methods=['GET', 'POST'])
def login():
    # return redirect(url_for('get_examples'))
    return render_template("login/index.html")



@app.route("/logout")
@login_required
def logout():
    session.pop('user')
    return redirect(url_for('login'))


# Route to handle form submission
@app.route('/authenticate', methods=['POST'])
def authenticate():
    print(request.form)
    username = request.form['username']
    password = request.form['password']

    password = password.strip()
    username = username.strip()
    user_id = users_db.get_userid(username=username)
    if user_id:
        user_passwd = users_db.get_password(username=username)
        if  password == user_passwd:
            session['user'] = username
            return redirect(url_for('home'))
        else:
            info = f"{get_time(string_obj= True)}\tUser {session.get('user')} wrong passwd {session.get('passwd')}"
            log_str("wrong passwd.txt" , message=info)
            return redirect(url_for('login'))
    else:
        print("creating aa new account")
        return redirect(url_for("register"))



@app.route("/register")
def register():
    return render_template("login/adduser.html")



@app.route("/adduser" ,  methods=['POST'])
def add_user():
    username = request.form['username']
    password = request.form['password']

    if users_db.get_userid(username=username):
        return redirect(url_for("login"))
    users_db.add_user(username=username , password=password)
    return redirect(url_for("home"))


@app.route("/link/<video_id>")
@login_required
def get_file_from_dir(video_id):
    file_path = Path(db_indexer.get_full_path(video_id))
    return send_from_directory (file_path.parent , file_path.name)


def get_file_link(video_id):
    with current_app.test_request_context():
        file_url = url_for("get_file_from_dir" , video_id=video_id)
    return file_url


@app.route("/home")
@login_required
def home():
    set_current_url(scheme = 'http',
                    server_addres=request.host ,
                    path=request.path)

    current_time = time.localtime()
    formated_time = time.strftime("%Y/%b/%d  %H:%M" , current_time)
    # formated_time = str(request.remote_addr)
    movies = db_indexer['MOVIES']
    return render_template("home7ch.html" , movies = movies , time_now = formated_time)


@app.route("/download/<content_id>", methods=["GET"])
@login_required
def download_video(content_id):

    filename = db_indexer.get_full_path(content_id=content_id)
    filename = Path(filename)
    # print("here is file name" , filename)
    if not filename.is_file():
        print("doint not find" , filename)
        return make_response("Video not found", 404)

    video_path = filename
    headers = request.headers

    if not "range" in headers:
        chunk_size = (10 ** 6) * 3
        # Client hasn't requested a byte range, send the first chunk of video
        file_size = os.path.getsize(video_path)
        start = 0
        end = min(1024 * 1024 - 1, file_size - 1)  # Send first 1 MB
        content_length = end - start + 1

        with open(video_path, "rb") as f:
            f.seek(start)
            video_chunk = f.read(content_length)

        response = make_response(video_chunk, 206)  # Use 206 Partial Content
        response.headers.set("Content-Type", "video/mp4")
        response.headers.set("Content-Range", f"bytes {start}-{end}/{file_size}")
        response.headers.set("Accept-Ranges", "bytes")
        response.headers.set("Content-Length", content_length)

        # Set additional headers to prevent caching and force download as a stream
        response.headers.set("Cache-Control", "no-cache, no-store, must-revalidate")
        response.headers.set("Pragma", "no-cache")
        response.headers.set("Expires", "0")

        headers = response.headers
        # print("here are headers" , headers)
        # return send_file(video_path, mimetype="video/mp4")
        # return current_app.response_class(status=400)

    else:
        size = os.stat(video_path)
        size = size.st_size
        # print("here are headrs 2" , headers)
        chunk_size = (10 ** 6) * 3 #1000kb makes 1mb * 3 = 3mb (this is based on your choice)
        start = int(re.sub("\D", "", headers["range"]))
        end = min(start + chunk_size, size - 1)

        content_lenght = end - start + 1
        headers = {
            "Content-Range": f"bytes {start}-{end}/{size}",
            "Accept-Ranges": "bytes",
            "Content-Length": content_lenght,
            "Content-Type": "video/"
            }

    def get_chunk(video_path, start, chunk_size):
        with open(video_path, "rb") as f:
            f.seek(start)
            chunk = f.read(chunk_size)
        return chunk


    filename = str(Path(filename).name)
    headers = {'Content-Disposition': f'attachment; filename="{filename}"'}

    # Return the file with the updated headers
    # print("here is downloaifng" , video_path)
    return send_file(video_path, as_attachment=True,download_name=filename)
    # return current_app.response_class(get_chunk(video_path, start,chunk_size), 206, headers)


@app.route("/templates/static/<filename>")
def get_template_min(filename):
    return send_from_directory("static/", filename)


@app.route('/stream_video/<video_id>')
@login_required
def stream_video(video_id):
    set_current_url(scheme = 'http',
                    server_addres=request.host ,
                    path=request.path)
    video_url =get_file_link(video_id)

    if db_indexer.determine_if_downloadable(content_id=video_id):
        content =  db_indexer['MOVIES']
    else:
        content , _ =  db_indexer['STREAM']
    return render_template("stream_movies.html" , video_link = video_url , content =content)


@app.route('/image/<filename>')
def get_image(filename):
    image_id = int(filename)
    image_path = db_indexer.get_image_src(image_id)
    if image_path != None:
        image_name = Path(image_path).name
        image_dir = Path(image_path).parent

        return send_from_directory(image_dir , image_name)


@app.route("/admin")
@login_required
def admin():
	return redirect(url_for("home"))


@app.route("/stream")
@login_required
def see_streaming():
    set_current_url(scheme = 'http',
                    server_addres=request.host ,
                    path=request.path)
    streaming_content = db_indexer['STREAM']
    movies , series = streaming_content
    series_content = db_indexer.get_distinc_series(downloadable=False)
    return render_template("stream.html" , movies=movies ,series=series_content ,  time_now = get_time())


@app.route("/games")
# @login_required
def get_examples():
    set_current_url(scheme = 'http',
                    server_addres=request.host ,
                    path=request.path)
    games_data = db_indexer['GAMES']
    return render_template("games.html" , time_now = get_time() , content = games_data)



@app.route("/specific_games/<game_id>")
def view_specific_game(game_id):
    game_name = (db_indexer[game_id])[0][1]
    return render_template("save_game.html" ,content_id = game_id , content_name =  game_name )





@app.route("/g_download/<game_id>" ,  methods=['POST'])
# @true_login_required
def get_game(game_id):
    option = request.form.get('option' , 'local')
    if option =='download':
        # return redirect(")
        pass
    elif option == 'loca':
        pass
    game_path = Path(db_indexer.get_full_path(game_id))
    return send_from_directory(game_path.parent , game_path.name)


@app.route("/series")
@login_required
def show_available_series():
    set_current_url(scheme = 'http',
                    server_addres=request.host ,
                    path=request.path)
    series_content = db_indexer.get_distinc_series(downloadable=True)
    return render_template("series.html" , content = series_content)


@app.route("/specific_series/<series_id>")
@login_required
def series_list(series_id):
    set_current_url(scheme = 'http',
                    server_addres=request.host ,
                    path=request.path)
    
    series_name = db_indexer.get_series_name(series_id)
    content = sorted(db_indexer.get_full_series(series_name=series_name))
    vid_link = get_file_link(series_id)
    full_path = db_indexer.get_full_path(series_id)
    if full_path:
        video_type = full_path.split(".")[-1]
    else:
        video_type = 'mp4'
    return render_template("stream_series.html" , video_link = vid_link , content = content , video_id= series_id)



# @app.route("/stream_video_premium/image/<content_id>")
# @app.route("/specific_series/image/<content_id>")
# @app.route("/stream_video/image/<content_id>")
# @app.route("/g_download/image/<content_id>")
# def re_route_image(content_id):
#     print("rerouting the wrong way" , content_id)
#     return redirect   (url_for(f"get_image" , filename = content_id))




@app.route("/cart/<userid>")
@login_required
def cart(userid):
    return render_template("watchlist.html")



##new features



def return_to_parent(content_id):
    if not  str(content_id).isdigit():
        its_series = True
        content_id = db_indexer.get_random_series_id(series_name=content_id)
    else:
        its_series = False

  
    content_type = db_indexer.get_content_type(int(content_id))

    if content_type == 'MOVIES':
        return redirect(url_for('home'))
    if content_type == 'SERIES':
        if its_series:
            return redirect(url_for("show_available_series"))
        else:
            return redirect(url_for("series_list" , series_id= content_id))
    
    if content_type == 'GAMES':
        return redirect(url_for("get_examples"))
    if content_type == 'STREAM':
        is_movie = db_indexer.is_movie(content_id=content_id)
        if is_movie:
             return redirect(url_for("see_streaming"))
        else:
            if its_series:
                return redirect(url_for("see_streaming" )) 
            return redirect(url_for("series_list" ,series_id= content_id) ) 


@app.route('/buy/<content_id>')
@login_required
def buy_s(content_id):
    user_name = session.get("user")
    user_id = users_db.get_userid(username=user_name)
    print("here is user name" , user_name)

    user_unique = UniqueUser(db_folder=CONTENT_LOCATION  , user_name=user_name)

    if str(content_id).isdigit():
        users_db.update_consumer_table(user_id=user_id , content_id=content_id)
        user_unique.update_consumer_table(content_id=content_id)
    else:
        all_series = db_indexer.get_full_series(content_id)
        print(all_series)
        if all_series:
            for item in all_series:
                users_db.update_consumer_table(user_id=user_id , content_id=item[0])
                user_unique.update_consumer_table(content_id=item[0])
    
    return return_to_parent(content_id=content_id)

@app.route("/up")
def up():
   return render_template("upload.html")


# @app.route("/upload", methods=['POST'])
# def upload():
#     files = request.files.getlist('files')
#     for file in files:
#         file_path = UPLOAD_DIR / file.filename
#         file_path.parent.mkdir(parents = True , exist_ok = True)
#         if file_path.is_file() or 1 == 1:
#             file.save(str(file_path))
#         print(f"Uploaded {file_path}")

#     return render_template("upload.html")



@auth.verify_token
def verify_token(token):
    if token in TOKENS:
        return TOKENS[token]

@app.route("/upload", methods=['POST'])
@auth.login_required
def upload():
    current_user = auth.current_user()
    print('files' in request.files)
    if 'files' in request.files:
        # File upload
        files = request.files.getlist('files')
        uploaded_files = []
        for file in files:
            file_path =file_path = UPLOAD_DIR / file.filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file.save(str(file_path))
            uploaded_files.append(str(file_path))
            print(f"Uploaded {file_path}")
        
        return jsonify({"message": "Files uploaded successfully", "files": uploaded_files}), 200
    
    elif request.is_json:
        # JSON data upload
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data received"}), 400
        
        if 'file-name' in request.headers:
            filename = Path(request.headers['file-name'])/f"{current_user}.json" 
        else:
            filename = f"{current_user}_{get_time()}.json"


        file_path = UPLOAD_DIR / filename
        file_path.parent.mkdir(parents=True , exist_ok=True)
        try:
            if file_path.exists() and file_path.is_file():
                saved_state = save_load_program_data(file_path)
            else:
                saved_state={}
    
            saved_state.update(data)
            save_load_program_data(path=file_path , mode='w' , data=saved_state )

            return jsonify({"message": f"Data saved successfully to {filename}"}), 200
        except Exception as e:
            return jsonify({"error": f"Failed to save data: {str(e)}"}), 500
    
    else:
        return jsonify({"error": "Unsupported content type"}), 400






@app.route("/checkout" , methods = ['GET'])
def show_checkout():
   
    server_addres = request.host
    user_name = session.get("user")
    
    back_link= session.get("current_url")
    
    params = {'user_name':user_name,"server_addres":back_link}
   
    check_out_page_url = set_current_url(scheme='http',
                                         server_addres=server_addres +":8501",
                                         query_params=params,
                                         path='' , set_url=False )
    

    return redirect(check_out_page_url)



def generate_limited(file_path, start, end):
    """Generate file in chunks with a limited download speed and specified range."""
    with open(file_path, "rb") as file:
        file.seek(start)
        while True:
            data = file.read(min(end - start + 1, 1024))
            if not data:
                break
            yield data


def claculate_sleep_time(file_size):
    max_speed = 1024*700
    time_in_sec = file_size /(max_speed)
    time_in_minutes = time_in_sec / 60
    time_in_hrs = time_in_minutes/60

    return time_in_sec




@download_limiter.limit('3/minute')
@app.route("/send_file/<path>")
def send_file(path):
    """Serve a media file with a limited download speed, getting the file path and range from the request parameters."""
    file_path = db_indexer.get_full_path(int(path))
    
    if not file_path:
        return "File path is missing", 400


    if not os.path.isfile(file_path):
        return "File not found", 404

    # Get the requested range
    range_header = request.headers.get("Range", None)
    if range_header:
        start, end = map(int, range_header.replace("bytes=", "").split("-"))
    else:
        start = 0
        end = os.path.getsize(file_path) - 1

    # Set the `Content-Range` header to inform the client about the range of the response
    content_range = f"bytes {start}-{end}/{os.path.getsize(file_path)}"
    headers = {
        "Content-Range": content_range,
        "Accept-Ranges": "bytes",
        "Content-Length": str(end - start + 1),
    }

    def generate_limited_response():
        """Generate file in chunks with a limited download speed and specified range."""
        start_time = time.time()
        bytes_sent = 0

        file_size = os.path.getsize(file_path) - start
        for data in generate_limited(file_path, start, end):
            delay = claculate_sleep_time(file_size=file_size)
            if file_size > 0:
                time.sleep(1/delay)
            bytes_sent += len(data)
            yield data

    response = Response(generate_limited_response(), headers=headers, mimetype=("video/mp4" if file_path.endswith(".mp4") else "video/x-msvideo"))

    filename = os.path.basename(file_path)
    response.headers["Content-Disposition"] = f"attachment; filename*=UTF-8''{filename}"

    return response


@app.route('/watchlist' , methods = ['GET' , 'POST'])
@login_required
def route_download():
    set_current_url(scheme = 'http',
                    server_addres=request.host ,
                    path=request.path)
    current_user = UniqueUser(db_folder=CONTENT_LOCATION , user_name=session.get('user'))
    files = current_user.get_paid_content(ids_only=True)
    files = current_user.classify_payed_cont(ids=files)
    
    files['GAMES'] =  [(db_indexer.get_content_name(i) ,i)for i in files['GAMES'] ]
    files['MOVIES'] =  [(db_indexer.get_content_name(i) ,i)for i in files['MOVIES'] ]
    
    series_dict = {}
    for series_name in files['SERIES']:
        series_id = files['SERIES'][series_name]
        series_dict[series_name] = [(db_indexer.get_content_name(i) , i) for i in series_id]
        
    files['SERIES'].update(series_dict)
    print(files['SERIES'])
    return render_template('watchlist.html', files=files)
































