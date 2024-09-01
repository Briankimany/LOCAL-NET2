
import streamlit as st
import config
from users_data import UniqueUser
from datetime import datetime
import os
import pandas as pd

now = datetime.now().strftime("%Y-%m-%d")
orders_path = config.CONTENT_LOCATION /"ORDERS"/ now


if "page_is_wide" not in st.session_state:
    st.set_page_config(layout='wide')
    st.session_state.page_is_wide = True

if orders_path.exists():
    orderids = os.listdir(orders_path)

    st.session_state['USERS']={}
    names = os.listdir(orders_path)
    content = []
    
    DENIED_ORDERS = []
    for order_id in names:
        l = os.path.join(orders_path/order_id)
        with open(l , 'r') as f:
            name = f.read()

        orderid = order_id.replace(".text" , "")
        orderid = orderid.strip()
        name = name.strip()

       
        user_data = UniqueUser(db_folder=config.CONTENT_LOCATION , user_name=name)
        status = user_data.get_cart_status(orderid=orderid)

        if status == 'VERIFIED' or status == None:
            continue
        else:
            if status == 'DENIED':
                DENIED_ORDERS.append(user_data)
            else:
                content.append(user_data) 
                st.session_state['USERS'][orderid]=user_data


    def make_changes():
        USERS_DATA = st.session_state['USERS']
        for  order_id , current_user in USERS_DATA.items():
            
            key = f"{order_id}_status"
            status= st.session_state.get(key , None)
           
            if status == None:
               pass
            else:
                current_user.update_cart(price=None ,content_ids=None , status=status , orderid=order_id , phone = None , time_initiated = None)
        
    st.page_link(label="pagegeg" ,page="http://localhost/stream")
    with st.container():
        st.button(label="APPLY",on_click=make_changes)
        for orderid , user in st.session_state['USERS'].items():
            verify , annalysis = st.columns(2 , gap='medium')
            order_details = user.check_order_details(orderid=orderid)
            with verify:
                order_details['name']= user.name
                order_details = pd.DataFrame([order_details])
                st.table(order_details)
            with annalysis:
                status = st.selectbox("VERIFY USER",['VERIFIED' , 'DENIED' ,'WAITING'] , key=f"{orderid}_status" ,
                                    index= None ,placeholder="SELECT STATE")
                
            st.divider()
    
   
