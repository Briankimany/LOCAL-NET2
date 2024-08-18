
# import streamlit as st
# from utils import get_time
# from users_data import UniqueUser
# import config

# import st_static_export as sse

# # user = UniqueUser(db_folder=config.CONTENT_LOCATION ,user_name="Gatu")

# # st.title("CHECK OUT")
# # st.subheader(get_time())

# # st.header("HELLO " )
# # st.dataframe(user.format_user_content())



# import streamlit as st
# from utils import get_time
# from users_data import UniqueUser
# import config

# # Initialize the user
# user = UniqueUser(db_folder=config.CONTENT_LOCATION, user_name="Gatu")

# # Set up the Streamlit page
# st.set_page_config(page_title="Checkout", layout="wide")

# # Title and Header
# st.title("CHECK OUT")
# st.subheader(get_time())
# st.header("HELLO " + user.name)

# # Display user content
# st.dataframe(user.format_user_content())

# # Checkout section
# st.sidebar.header("Checkout Details")

# # Get user's selected items for checkout
# selected_items = st.multiselect(
#     "Select items for checkout",
#     options=user.get_item_list(),  # Assume this method returns a list of items
#     default=[]
# )

# # Display selected items
# st.write("Selected Items:", selected_items)

# # Button to proceed with checkout
# if st.button("Proceed with Checkout"):
#     if selected_items:
#         success = user.checkout(selected_items)  # Implement this method in UniqueUser
#         if success:
#             st.success("Checkout successful!")
#         else:
#             st.error("There was an error during checkout. Please try again.")
#     else:
#         st.warning("Please select at least one item to checkout.")







from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('checkout.html')

@app.route('/submit', methods=['POST'])
def submit():
    item = request.form.get('item')
    quantity = request.form.get('quantity')
    # Process the checkout (e.g., save to database, etc.)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
