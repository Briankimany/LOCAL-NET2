
from flask import Flask
from flask import  redirect, url_for , render_template , send_from_directory , make_response , request  , current_app , send_file , session , render_template_string
import re
import os
import time
from pathlib import Path
from utils import save_load_program_data
from functools import wraps


from database import DataBaseIndex
from users import Users
import logging


from config import CONTENT_LOCATION , DATABASE_LOCATION , USER_DB_LOCATION , UPLOAD_DIR
from pathlib import Path


users_db = Users(CONTENT_LOCATION)
app = Flask(__name__)
app.config['STATIC_FOLDER'] = os.path.abspath('templates/static')


app.secret_key='KIMANI'
db_indexer = DataBaseIndex(db_path=DATABASE_LOCATION)

app.logger.setLevel(logging.DEBUG)  # Set the logging level (DEBUG, INFO, etc.)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = logging.StreamHandler()  # Log to console
handler.setFormatter(formatter)
app.logger.addHandler(handler)





# def login_required(func):
#     @wraps(func)
#     def decorated_function(*args, **kwargs):
#         # print("calling the decorated funtion")
#         if 'user' not in session:
#         if 'user' not in session or session['user'].lowwer() != 'Ajay':
#             return redirect(url_for('get_examples'))
#         return func(*args, **kwargs)
#     return decorated_function


def login_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        # print("calling the decorated funtion")
        if 'user' not in session:
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return decorated_function





def true_login_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        # print("calling the decorated funtion")
        if 'user' not in session:
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return decorated_function



def get_time():
    current_time = time.localtime()
    formated_time = time.strftime("%Y/%b/%d  %H:%M" , current_time)
    return formated_time


@app.route("/" ,  methods=['GET', 'POST'])
def login():
    # return redirect(url_for('get_examples'))
    return render_template("login.html")


# Route to handle form submission
@app.route('/authenticate', methods=['POST'])
def authenticate():

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
            info = f"User {session.get('user')} wrong passwd {session.get('passwd')}"
            return redirect(url_for('login'))
    else:
        print("creating aa new account")
        return redirect(url_for("register"))



@app.route("/register")
def register():
    return render_template("register.html")



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

    streaming_content = db_indexer['STREAM']
    movies , series = streaming_content
    series_content = db_indexer.get_distinc_series(downloadable=False)
    # print(series_content)
    return render_template("stream.html" , movies=movies ,series=series_content ,  time_now = get_time())


@app.route("/games")
# @login_required
def get_examples():
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
    series_content = db_indexer.get_distinc_series(downloadable=True)
    return render_template("series.html" , content = series_content)


@app.route("/specific_series/<series_id>")
@login_required
def series_list(series_id):

    series_name = db_indexer.get_series_name(series_id)
    content = sorted(db_indexer.get_full_series(series_name=series_name))
    vid_link = get_file_link(series_id)
    full_path = db_indexer.get_full_path(series_id)
    if full_path:
        video_type = full_path.split(".")[-1]
    else:
        video_type = 'mp4'
    return render_template("stream_series.html" , video_link = vid_link , content = content)



@app.route("/stream_video_premium/image/<content_id>")
@app.route("/specific_series/image/<content_id>")
@app.route("/stream_video/image/<content_id>")
@app.route("/g_download/image/<content_id>")
def re_route_image(content_id):
    return redirect   (url_for(f"get_image" , filename = content_id))




@app.route("/cart/<userid>")
@login_required
def cart(userid):
    return render_template("watchlist.html")



##new fwtures


@app.route('/buy/<content_id>')
@login_required
def buy_s(content_id):

    user_name = session.get("user")
    user_id = users_db.get_userid(username=user_name)
    if str(content_id).isdigit():
        users_db.update_consumer_table(user_id=user_id , content_id=content_id)

    else:
        all_series = db_indexer.get_full_series(content_id)
        if all_series:
            for item in all_series:
                print(f"adding {item[1]} to db")
                users_db.update_consumer_table(user_id=user_id , content_id=item[0])

    return redirect(url_for(f"cart" , userid = user_id))


@app.route("/up")
def up():
   return render_template("upload.html")
@app.route("/upload" , methods = ['POST'])
def upload():

    file = request.files['file']
    file_path = Path(UPLOAD_DIR) / file.filename

    file.save(str(file_path))

    return render_template("upload.html")













































