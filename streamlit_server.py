

import streamlit as st
import pandas as pd
from config import CONTENT_LOCATION
from users_data import UniqueUser
import config
from database_index import DataBaseIndex
from streamlit_option_menu import option_menu
from utils import get_time

import streamlit_shadcn_ui as ui
from streamlit_shadcn_ui import alert_dialog , card , hover_card

from PIL import Image
import requests
import json
from urllib.parse import urlparse


params =list((st.query_params.to_dict().items())) 

if "page_is_wide" not in st.session_state:
    st.set_page_config(layout='wide')
    st.session_state.page_is_wide = True

st.logo(Image.open("/home/ajay/Pictures/ai pics/imasaaage (2).jpeg"))

if len(params) >=1:
    name = params[0][1]
    return_server_addres = params[1][1]

if 'name' not in st.session_state:
    st.session_state.name = name
    st.session_state.return_server_addres = return_server_addres


name = st.session_state.name
return_server_addres = st.session_state.return_server_addres

user = UniqueUser(db_folder=CONTENT_LOCATION , user_name=name)
db_indexer = DataBaseIndex(db_path=config.DATABASE_LOCATION)


st.markdown("""
    <style>
    /* Page Background */
    body {
        background-color: #f0f0f5;
    }
    /* Header */
    .header {
        background: linear-gradient(to right, #6a11cb, #2575fc);
        padding: 20px;
        text-align: center;
        color: white;
        font-size: 2.5em;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2);
    }
    /* Grid container */
    .grid-container {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 20px;
        padding: 10px;
    }
    /* Grid item */
    .grid-item {
    
        border-radius: 10px;
        box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
        padding: 15px;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .grid-item:hover {
        transform: scale(1.05);
        box-shadow: 0px 8px 16px rgba(0, 0, 0, 0.2);
    /* Download Button */
    .download-btn {
        background-color: #4CAF50;
        color: black;
        padding: 10px 20px;
        text-align: center;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        font-size: 1em;
    }
    .download-btn:hover {
        background-color: #45a049;
    }
    </style>
    """, unsafe_allow_html=True)
st.markdown(f"<div class='header'>Checkout Page for {name}</div>", unsafe_allow_html=True)


def get_content_price(content_id):
    content_id = int(content_id)
    content_type = db_indexer.get_content_type(content_id= content_id)
    content_path = db_indexer.get_full_path(content_id=content_id)

    if content_type == "STREAM":
        content_type = "SERIES" if "SERIES" in content_path else "SMOVIES"

    if content_type == 'GAMES':
        price = 300

    elif content_type== "MOVIES":
        price = 10
    
    elif content_type == 'SERIES':
        series_name = db_indexer.get_content_name(content_id=content_id)
        price = 30 / len(db_indexer.get_full_series(db_indexer.get_series_name(series_name=series_name , parent=True)))
    elif content_type == "SMOVIES":
        price = 20
    
    return price


def remove_items():
    removed =[]
    for i in st.session_state.items_to_remove:
        user.remove_content(content_id=int(i))
        removed.append(i)
    for i in removed:
        if st.session_state.items_to_remove:
            st.session_state.items_to_remove.remove(i)
    df = user.format_user_content(json_cont=False)
    st.session_state.user_df = df

def clean_name(name):
    return name


st.session_state['show_games'] = True
st.session_state['show_movies'] = True
st.session_state['show_series'] = True


class Cart:
    def __init__(self , df:pd.DataFrame) -> None:
        self.update(df)

    def set_prices(self):
         self.df['PRICES'] = self.df['Content ids'].map(get_content_price)

    def form_cart(self):
        sample_df =  self.df[['Content ids' ,'type' ,'PRICES']]
        results = {}
        
        self.content_ids = []       
        results['GAMES'] = []
        results['MOVIES']=[]
        results['SERIES'] = {} 
        for index , (content_id , content_type,price) in sample_df.iterrows():
            self.content_ids.append(content_id)

            item_name =db_indexer.get_content_name(content_id=int(content_id))

            if content_type == 'STREAM':
                path = db_indexer.get_full_path(content_id=int(content_id))
                if "MOVIES" in str(path):
                    results['MOVIES'].append({'id':content_id , "cost":price ,
                                              "Item name":clean_name(item_name) , 'Quantity':1})
                elif 'SERIES' in str(path):
                    series_name = db_indexer.get_series_name(series_name=item_name)
                    if series_name not in  results['SERIES']:
                         results['SERIES'][series_name] = []

                    results['SERIES'][series_name].append((content_id ,clean_name(item_name)))

            elif content_type == "SERIES":
                series_name = db_indexer.get_series_name(series_name=item_name)
                if series_name not in  results['SERIES']:
                        results['SERIES'][series_name] = []
                results['SERIES'][series_name].append((content_id ,clean_name(item_name)))

            elif content_type == 'GAMES':

                results['GAMES'].append({'id':content_id ,'cost':price,'Item name':clean_name(item_name),  'Quantity':1})

        return results
    
    def update(self , df):
        self.df = df
        self.set_prices()
        self.cart_items = self.form_cart()

        self.movies()
        self.series()
        self.games()
        return self


    def games(self):
        games = self.cart_items['GAMES']
        if len(games) == 0:
            st.session_state.show_games = False
            games = {'Item name':[] , 'cost':[],'Quantity':[]}
        df = pd.DataFrame(games)
        return df[["Item name" , 'cost' , 'Quantity']]
    def series(self):
        series = self.cart_items['SERIES']

        if len(list(series.items()))==0:
            st.session_state.show_series = False
            series = {'Item name':[] , 'cost':[],'Quantity':[]}
            series_df = series
        else:
            series_df = []
            for series_name in series:
                num_episodes = len(series[series_name])
                if num_episodes >=6:
                    price = 30
                else:
                    price = None
                    for i  , _ in series[series_name]:
                        if i in self.content_ids:
                            self.content_ids.remove(i)

                series_df.append({'Item name':series_name , 'cost':price ,'Quantity':num_episodes})


        return  pd.DataFrame(series_df)[['Item name' , 'cost','Quantity']]
    
    def movies(self):
        movies =self.cart_items['MOVIES']
        if len(movies) == 0:
            st.session_state.show_movies = False
            movies = {'Item name':[] , 'cost':[],'Quantity':[]}
        df = pd.DataFrame(movies)
        return   df[['Item name' , 'cost','Quantity']]


def post(user_name ,price, phone,content_ids=None):
    headers = { 'Content-Type': 'application/json'}

    response = requests.post(url='http://127.0.0.1:5005/verify' , data =json.dumps({"user_name":user_name,
                                                                                "amount":str(price),
                                                                                'ids':content_ids,
                                                                                'phone':str(phone)}) , headers=headers)
    return response


@st.dialog("Confirming check out")
def confirm(price , username , content_ids):
    st.header(f"Confirm {price} has been payed to 0793536684")
    phone = st.text_input(label="ENTER YOUR PHONE NUMBER" ,key = "client_phone" , placeholder="0722....")
    
    link_parts = urlparse(return_server_addres)
    full_link = f"{link_parts.scheme}://{link_parts.netloc}/watchlist"

    if st.button("YES") and len(phone) >= 3:
        st.write("Kindly wait for verification ....")
        response = post(user_name=username , price = price , content_ids=content_ids , phone=phone)

        if int(response.status_code)==101:
            st.warning("COULD  NOT PROCCES VERIFICATION ...☹️☹️☹️")
        else:
            message = json.loads(response.content)
            if message['response'] == 'VERIFIED':
                st.balloons()
                st.write("Verified ..... ")
                user.update_cart(price=None , content_ids=message.get("PAYED_IDS" , []) ,  orderid= message.get('orderid' , None) ,
                                  status=None , phone=None , time_initiated=None , update_payed_for=True)
                
                cehcked_ids =message.get('PAYED_IDS' , [])

                st.session_state.items_to_remove += cehcked_ids
                remove_items()
                
                st.link_button("My WatchList" , url=full_link)
                # st.rerun()
            elif message['response'] == 'DENIED':
                st.write("COULD NOT CONFIRM PURCHASE ....")
                st.link_button("My WatchList" , url=full_link)
            elif  message['response'] == 'WAITING':
                st.write("Verification could not be done  in 2 minute")
                st.write("Visit your store to check it out they will be ther in a minute")
                st.link_button("My WatchList" , url=full_link)

    
    else:
        pass
    
    
   
        


with st.container():
    if 'name' in st.session_state:
            if "user_df" not in st.session_state:
                df = user.format_user_content(json_cont=False)
                if len(df['Content ids']) == 0:
                    st.warning("No data found")
                st.session_state.user_df = df

            st.markdown("<div class='grid-container'>", unsafe_allow_html=True)

            with st.sidebar:
                st.link_button(label="BACK TO HOME" , url=return_server_addres , help='Go back to contan page')
                selected = option_menu("Main Menu", ["Home", 'Settings'], 
                    icons=['house', 'gear'], menu_icon="cast", default_index=0)
                if selected == 'Settings':
                    st.title("HELLO ", user.name)
                    st.data_editor(user.format_user_content()['Content ids'])

            if 'items_to_remove' not in st.session_state:
                st.session_state.items_to_remove = []


            categories = st.session_state.user_df.groupby('type')
            finer_categories = categories[['names' , 'Content ids']]
    
            st.markdown("""<style>
                        button[data-baseweb="tab"] {
                        font-size: 50px;
                        margin: 0;
                        width: 100%;
                        }
                        </style>""" , unsafe_allow_html=True)
            
            pay_tab  , view_tab = tab = st.tabs(tabs=['PAYOUT' , 'MOFIFY CHART'])
            
            
            with pay_tab:
              
                user_cart = Cart(df = st.session_state.user_df) 
       
                user_cart = user_cart.update(st.session_state.user_df)
                column1 , column2 = st.columns(2 , vertical_alignment='top' , gap= 'medium')

                
                total_price = 0
                with column1:
                    if st.session_state.show_games:
                        with st.container():
                            st.header("GAMES")
                            st.table(data=user_cart.games())
                        total_price += user_cart.games()['cost'].sum()


            
                    if st.session_state.show_movies:
                        with st.container():
                            st.header("MOVIES")
                            st.table(data=user_cart.movies())
                        total_price+= user_cart.movies()['cost'].sum()

                        
                    if st.session_state.show_series:
                        with st.container():
                            st.header("SERIES")
                            st.table(data=user_cart.series())

                        total_price += user_cart.series()['cost'].sum()

               
                with column2:
                    st.divider()
                    st.header("CHECKING OUT")
                    st.metric(label="Total Price", value=f"Ksh {total_price:.2f}")
                    st.divider()
                    st.header(f"PAY {total_price}  VIA POCHI LA BIASHARA")
                    st.header("TO:  0793536684 ")
                    st.warning("kindly  use pochi for guaranteed verification of payment")
                    st.divider()

                    st.link_button(label = "ADD MORE" , url = st.session_state.return_server_addres)
                    if st.button("COMPLETE"):
                        confirm(price=total_price , username =  st.session_state.name , content_ids=user_cart.content_ids) 

            

            with view_tab:
                num_columns = st.slider(label="num columns" , min_value=1 , max_value=10 , value=3) 
                for key in finer_categories.groups:
                    group_content = finer_categories.get_group(key)
                    with st.container():
                        st.header(key)
                        cols = st.columns(num_columns)
                        for i, (index, row) in enumerate(group_content.iterrows()):
                            item_class = key
                            # Determine the column index to place the item
                            col_index = i % num_columns
                            with cols[col_index]:
                                st.markdown("<div class='grid-item" ,  unsafe_allow_html=True)
                                content_id = row['Content ids']
                                name = row['names']
                                image = db_indexer.get_check_out_image(content_id=int(content_id) , size=(224 , 224))
                                st.image(image=image)

                                if st.checkbox(label="remove" , key=f"Checkbox_{content_id}"):
                                    if content_id not in st.session_state.items_to_remove:
                                        st.session_state.items_to_remove.append(content_id)
                                else:
                                    if content_id in st.session_state.items_to_remove:
                                        st.session_state.items_to_remove.remove(content_id)
                                name = name + str(content_id)
                                st.subheader(name)
        
                                st.markdown("</div>",  unsafe_allow_html=True)

                    st.markdown("</div>", unsafe_allow_html=True)

                st.button(label='APPLY' , on_click=remove_items)
      
    else:
        st.page_link("http://localhost/games" , label="Back o main page" , icon="🚨")
        st.link_button(url="http://localhost" , label="Back o main page")

