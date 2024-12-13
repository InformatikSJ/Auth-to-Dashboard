import pandas as pd
import requests
import csv
import streamlit as st
import plotly.express as px
from pycognito import Cognito

# Function to authenticate using PyCognito
def get_cognito_token(username, password, user_pool_id, client_id):
    try:
        # Create a Cognito user instance
        user = Cognito(user_pool_id, client_id, username=username)
        user.admin_authenticate(password=password)  # Authenticate the user
        st.write(f"Token: {user.access_token}")
        return user.access_token
    except Exception as e:
        st.error(f"Error during Cognito authentication: {str(e)}")
        st.stop()

# Function to fetch data via API with pagination
def fetch_data(api_url, token, api_key, params):
    all_data = []
    start = 0
    params['start'] = start

    while True:
        params['start'] = start
        headers = {
            "Authorization": f"Bearer {token}",
            "x-api-key": api_key  # Add the API key in the headers
        }
        response = requests.get(api_url, headers=headers, params=params)

        if response.status_code != 200:
            st.error(f"API Error: {response.status_code} - {response.text}")
            break

        # Parse the data
        data = response.json().get('products', [])
        if not data:
            break

        all_data.extend(data)
        start += len(data)

    return all_data

# AWS Cognito credentials
USERNAME = ""  # Replace with your Cognito username
PASSWORD = ""  # Replace with your Cognito password
USER_POOL_ID = ""  # Replace with your Cognito User Pool ID
CLIENT_ID = ""  # Replace with your Cognito app client ID

# API details
API_URL = ""
API_KEY = ""  # Replace with your API key
PARAMS = {

}

# Step 1: Authenticate with Cognito to get the token
st.title("Dashboard - Products")
st.write("Authenticating with AWS Cognito...")
TOKEN = get_cognito_token(USERNAME, PASSWORD, USER_POOL_ID, CLIENT_ID)

if not TOKEN:
    st.error("Failed to authenticate with AWS Cognito.")
    st.stop()

# Step 2: Fetch data from the API
st.write("Fetching data from the API...")
data = fetch_data(API_URL, TOKEN, API_KEY, PARAMS)

# Check data retrieval
if not data:
    st.error("No data retrieved. Check API parameters or permissions.")
    st.stop()

# Step 3: Save data to CSV
if len(data) > 0:
    csv_file = 'products.csv'
    with open(csv_file, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    st.success(f"Data saved to {csv_file}.")
else:
    st.error("No data available to create the CSV file.")
    st.stop()

# Step 4: Preview the data with pandas
df = pd.DataFrame(data)
st.write("Preview of the data:", df.head())

# Step 5: Interactive visualization with Plotly
st.write("Select a column to visualize:")
columns = df.columns.tolist()
selected_column = st.selectbox("Column to display", columns)

if selected_column:
    fig = px.histogram(df, x=selected_column, title=f"Distribution of {selected_column}")
    st.plotly_chart(fig)
