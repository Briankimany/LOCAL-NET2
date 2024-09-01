
from flask import Flask  , request , jsonify , session
import time


from datetime import datetime
from users_data import UniqueUser
import config
from utils import generate_order_id
from datetime import datetime
import playsound


app = Flask(__name__) 
app.secret_key='KIMANI'


def generate_orderid(name):
    now = datetime.now().strftime("%Y-%m-%d-%H%M")
    


@app.before_request
def make_noise():
    playsound.playsound('/home/ajay/Music/notifications/notificatio1.wav')

@app.route("/")
def home():
    return  "BAD REQUEST" , 400

@app.route("/verify" , methods = ['POST'])
def veirfy_user():
    try:
        data = request.get_json()

        user_name = data.get('user_name')
        price = data.get('amount')
        content_ids = data.get("ids")
        phone = data.get('phone')
    
        if "orderid" not in session:
            orderid = generate_order_id()
            session['orderid'] = orderid
        
        orderid = session.get('orderid')
        
        now = datetime.now().strftime("%Y-%m-%d")

        orderid_path = config.CONTENT_LOCATION /"ORDERS"/ now/f"{orderid}.text"
        orderid_path.parent.mkdir(parents= True ,exist_ok = True)

        with open(orderid_path , 'w') as file:
            file.write(user_name)

        time_initiated = datetime.now().strftime("%Y-%m-%d %H:%M")
        price = int(float(price))
        user = UniqueUser(db_folder=config.CONTENT_LOCATION , user_name=user_name)
        user.update_cart(price=int(price) , status="WAITING" , content_ids = content_ids , orderid=orderid , phone=phone , time_initiated=time_initiated)
        status = user.get_cart_status(orderid=orderid)
    
        if status == 'VERIFIED':
            message = 'VERIFIED'
            code = 200
        else:
            for i in range(10):
                status = user.get_cart_status(orderid=orderid)
                if status == 'WAITING':
                    message= "WAITING"
                    code = 300
                    time.sleep(12)
                elif status == 'DENIED':
                    message = 'DENIED'
                    code = 400
                    break
                elif status == 'VERIFIED':
                    message = "VERIFIED"
                    content_ids=data.get("ids")
                    code = 200
                    break
            
            if message != 'VERIFIED':
                content_ids = []
        
        response_data =  jsonify({"response":message , 'PAYED_IDS':content_ids,'orderid':orderid}), code

        return response_data
    except Exception as e:
        print(str(e))
        orderid = session.get('orderid' , 'none')
        message = "ERROR"
        return jsonify({"response":message , 'PAYED_IDS':[],'orderid':orderid}), 101




if __name__ == "__main__":
    app.run("0.0.0.0" , port=5005 , debug=True)













