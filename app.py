import streamlit as st
import pandas as pd
import pickle
import streamlit_authenticator as stauth
from pathlib import Path

st.set_page_config(page_title="CRIME PREDICTION", page_icon=":bar_chart:", layout="wide")

hide_bar= """
    <style>
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
        visibility:hidden;
        width: 0px;
    }
    [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
        visibility:hidden;
    }
    </style>
"""

# --- USER AUTHENTICATION ---
names = ["Siva Ramani", "Sarika Sri","Sangeetha"]
usernames = ["siva", "sarika","sangee"]

# load hashed passwords
file_path = Path(__file__).parent/"hashed_pw.pkl"
with file_path.open("rb") as file:
    hashed_passwords = pickle.load(file)

authenticator = stauth.Authenticate(names, usernames, hashed_passwords, "SIPL_dashboard", 'abcdef', cookie_expiry_days=30)
name, authentication_status, username = authenticator.login("Login", "main")

if st.session_state["authentication_status"]is False:
    st.error("Username/password is incorrect")
    st.markdown(hide_bar, unsafe_allow_html=True)

if st.session_state["authentication_status"]is None:
    st.warning("Please enter your username and password")
    st.markdown(hide_bar, unsafe_allow_html=True)


if st.session_state["authentication_status"]:
    # # ---- SIDEBAR ----
    st.sidebar.title(f"Welcome {name}")
    # st.sidebar.header("select page here :")

    st.sidebar.success("Select a page above.")
    hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
    st.markdown(hide_st_style, unsafe_allow_html=True)
    authenticator.logout("Logout", "sidebar")

    # Load the saved Random Forest model
    rf_model = pickle.load(open('knn_model_crime_name2.pkl', 'rb'))

    # Load the saved OneHotEncoder
    enc = pickle.load(open('one_hot_encoder.pkl', 'rb'))
 
    st.title('Crime Prediction App')

    st.subheader('Enter the following details to predict crime')

    # Get input from the user
    date_time = st.text_input('Date and Time (2023-05-14 12:30:00)')
    latitude = st.text_input('Latitude')
    longitude = st.text_input('Longitude')
    city = st.text_input('City')
    state = st.text_input('State')

    # Create a button for prediction
    if st.button('Predict'):
    # Check if input is not empty
        if not all([date_time, latitude, longitude, city, state]):
            st.error('Please enter all the details to predict crime')
        else:
            # Create a sample input from the user
            sample_input = pd.DataFrame({
                'date_time': [date_time],
                'latitude': [float(latitude)],
                'longitude': [float(longitude)],
                'city': [city],
                'state': [state]
                })

             # Preprocess the sample input
            sample_input['date_time'] = pd.to_datetime(sample_input['date_time'])
            sample_input['year'] = sample_input['date_time'].dt.year
            sample_input['month'] = sample_input['date_time'].dt.month
            sample_input['day'] = sample_input['date_time'].dt.day
            # Perform one-hot encoding for categorical variables
            cat_cols = ['city', 'state']
            encoded_cols = pd.DataFrame(enc.transform(sample_input[cat_cols]))
            encoded_cols.columns = enc.get_feature_names(cat_cols)
            # Handle unknown categories dynamically
            missing_categories = set(sample_input[cat_cols].values.flatten()) - set(enc.categories_[0])
            if missing_categories:
                for category in missing_categories:
                    encoded_cols[category] = 0

            sample_input.drop(cat_cols, axis=1, inplace=True)
            sample_input = pd.concat([sample_input, encoded_cols], axis=1)

             # Make predictions using the Random Forest model
            rf_prediction = rf_model.predict(sample_input)

             # Display the result
            st.subheader('Crime Prediction Result')
            if rf_prediction[0] == 0:
                st.write('No crime is predicted.')
            else:
                st.write('A crime is predicted:', rf_prediction[0])
