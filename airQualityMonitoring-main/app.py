import streamlit as st
import pandas as pd  
import plotly.express as px
import requests
import json
import time
import numpy as np
from datetime import datetime
import smtplib
from email.mime.text import MIMEText



st.set_page_config(page_title="Environment Dashboard", page_icon="🌐", layout='centered' )

# # Importing the CSS file
# st.markdown(
#     """
#     <link href='https://fonts.googleapis.com/css?family=Roboto' rel='stylesheet'>
#     <link href='Users/koyiljonvaliev/Desktop/IoTProject/style.css' rel='stylesheet'>
#     """,
#     unsafe_allow_html=True
# )

# # Add custom CSS to hide specific elements
# st.markdown(
#     """
#     <style>
#     #MainMenu {visibility: hidden;}
#     </style>
#     """,
#     unsafe_allow_html=True
# )

# with open('../style.css') as f:
#     st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


# things speak API connection 
@st.cache_data(ttl=6*10)  
def load_data():
    url = "https://api.thingspeak.com/channels/2363793/feeds.json?results=7600"   
    res = requests.get(url)
    if res.status_code == 200:
        feeds = res.json()['feeds']
        df = pd.DataFrame(feeds) 
        df['time'] = pd.to_datetime(df['created_at']).dt.tz_convert('Asia/Seoul')
        return df
    return None




# function to get current weather information from API 
@st.cache_data(ttl=6*10)  
def get_weather_data(api_key, locations):
    """Function to get weather data for a list of locations."""
    url = f"http://api.weatherapi.com/v1/current.json?key={api_key}"
    data_list = []

    for loc in locations:
        response = requests.get(url, params=loc['query'])
        if response.status_code == 200:
            data_list.append(response.json())
        else:
            st.error("Failed to fetch weather data.")
            return None

    return data_list


def display_weather_data():
    """Gets weather data for a list of locations and displays it in a formatted HTML layout."""
    api_key = "e6dc50b5df6142879d3165338231612"
    locations = [
        {
            "query": {
                "custom_id": "x",
                "q": "36.337214, 127.450889",
            }
        }
    ]

    data_list = get_weather_data(api_key, locations)

    for data in data_list:
        location = data['location']
        current = data['current']
        
        location_name = f"{location['name']}, {location['region']}, {location['country']}"
        local_time = location['localtime']
        temperature_c = current['temp_c']
        temperature_f = current['temp_f']
        humidity = current['humidity']
        wind = current["wind_mph"]

        # Outdoor data with emojis and time
        outdoor_data = {
            "Updated Time ⏰": local_time,
            "Location 🌍": location_name,
            "Temperature 🌡️": f"{temperature_c}°C / {temperature_f} °F",
            "Humidity 💧": f"{humidity}%",
            "Wind 💨": f"{wind} mph",
        }


    # Display outdoor data in a table
        message = "Outdoor Monitoring"
        st.markdown(f'<div style="padding:8px;"><p style="color:black; font-size:20px; font:bold;"> {message}</p></div>', unsafe_allow_html=True)
        st.table([outdoor_data])
    


    


# function to send email
def send_email(subject, message):
    sender_email = "545fdfdsfdf@gmail.com"  # Replace with your email address
    receiver_email = "xys@gmail.com"  # Replace with the recipient's email address
    password = "fdsfsdfdsfsdf"  # Replace with your email password or an app-specific password

    smtp_server = "smtp.gmail.com"
    smtp_port = 587  # Gmail's TLS port is 587

    # Create a message object
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver_email

    # Try to send the email
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")



# Thresholds
GAS_THRESHOLD = 800
LIGHT_THRESHOLD = 100
MIN_TEMP = 18  
MAX_TEMP = 25
MIN_HUMID = 30
MAX_HUMID = 60 



# warning message custom 
def custom_warning(message):
    st.markdown(f'<div style="background-color:red;padding:3px; margin-bottom:22px; border-radius:20px;"><p style="color:white; margin:5px;  text-align:center; font-size:22px;"> {message}</p></div>', unsafe_allow_html=True)



# Plot charts
def plot_charts(df, date):
    filtered_df = df[df['time'].dt.date == date]

    
    df = df.rename(columns = {
        "field1":"temprature",
        "field2":"humidity",
        "field3":"gas",
        "field4":"light"
    })
    current_time = df['time'].iloc[-1].strftime("%Y-%m-%d %H:%M")
    current_temperature = float(df['temprature'].iloc[-1])
    current_humidity = float(df['humidity'].iloc[-1])
    current_gas = float(df['gas'].iloc[-1])
    current_light = float(df['light'].iloc[-1])

    filtered_df = df[df['time'].dt.date == date]

    def celsius_to_fahrenheit(celsius):
        fahrenheit = (celsius * 9/5) + 32
        return fahrenheit
    
    fahrenheit_temp = celsius_to_fahrenheit(current_temperature)
    current_temperature_faranheit = f"{fahrenheit_temp}"



    indoor_data = {
    "Updated Time ⏰": current_time,
    "Temperature 🌡️": f"{current_temperature}°C/ {current_temperature_faranheit}°F",
    "Humidity 💧": f"{current_humidity}%",
    "Gas ⛽": f"{current_gas} %",
    "Light 💡": f"{current_light} lux"
     }






    # Alert Message

    low_temp_msg = f""" 
    🚨 The current temperature of {current_temperature}°C is below the minimum threshold of {MIN_TEMP}°C. This cold temperature is unhealthy and risky.  

    ✅ Actions: Turn up the thermostat to heat the room. Wear extra layers and limit exposure. Prolonged cold can lead to hypothermia and exacerbate illnesses.

    "Time ⏰": current_time,
    "Temperature 🌡️": f"{current_temperature}°C",
    "Humidity 💧": f"{current_humidity}%",
    "Gas ⛽": f"{current_gas} %",
    "Light 💡": f"{current_light} lux"
       
         """

    high_temp_msg = f"""  
    🚨 The current temperature of {current_temperature}°C is above the maximum threshold of {MAX_TEMP}°C. This hot temperature poses health risks.  

    ✅ Actions: Turn on the AC/cooler to lower the temperature. Stay hydrated. Avoid strenuous activity as heat exhaustion/stroke are possible. Seek medical help if feeling faint or confused. 

    Time: {current_time}
    Temprature: {current_temperature}°C
    Gas level: {current_gas}%
    Humidity level: {current_humidity}%
    Current light: {current_light} lux
        """

    low_humidity_msg = f"""
    🚨 The current humidity of {current_humidity}% is below the minimum threshold of {MIN_HUMID}%. This dry air can cause respiratory irritation.

    ✅ Actions: Use a humidifier to raise humidity levels. Drink plenty of water. Use nasal saline spray/balms to ease airway dryness. Consult your doctor if symptoms persist.   

    Time: {current_time}
    Temprature: {current_temperature}°C
    Gas level: {current_gas}%
    Humidity level: {current_humidity}%
    Current light: {current_light} lux
        """
    high_humidity_msg = f"""
    🚨 The current humidity of {current_humidity}% is above the maximum threshold of {MAX_HUMID}%. This excessive moisture promotes growth of mold, mildew and dust mites.

    ✅ Actions: Turn on the dehumidifier to lower moisture levels. Open windows regularly to ventilate rooms. Use exhaust fans when bathing/cooking. Clean any damp areas and check for leaks. Reduce indoor plants and aquariums if humidity doesn't decrease.

    Time: {current_time}
    Temprature: {current_temperature}°C
    Gas level: {current_gas}%
    Humidity level: {current_humidity}%
    Current light: {current_light} lux
        """

    high_gas_msg = f"""  
    🚨 The current gas level of {current_gas}ppm is higher than the safe threshold of {GAS_THRESHOLD}ppm. Exposure can cause headaches, nausea, or even loss of consciousness.

    ✅ Actions: Ventilate the room immediately. Turn off gas appliances and identify any leaks. Leave the area and seek medical help if feeling unwell. Call emergency services if leak is large.

    Time: {current_time}
    Temprature: {current_temperature}°C
    Gas level: {current_gas}%
    Humidity level: {current_humidity}%
    Current light: {current_light} lux
    """
    abnormal_light_msg = f"""
    🚨 The current light level of {current_light} lux is lower than 100 lux. Abnormal lighting can negatively impact health, sleep cycles, and eye comfort.   
    ✅ Actions: Dim harsh lighting or draw window coverings if over exposed. Seek medical guidance if eye strain or headaches occur. Consider adding extra lighting or timer systems to regulate lighting based on occupancy and sunlight availability.  

    Time: {current_time}
    Temprature: {current_temperature}°C
    Gas level: {current_gas}%
    Humidity level: {current_humidity}%
    Current light: {current_light} lux
    """


    low_temp_alert = " 🚨 Low temperature warning!"  

    high_temp_alert = " 🚨 High temperature alert!"
    
    low_humid_alert = " 🚨 Humidity too low!"

    high_humid_alert = " 🚨 Humidity too high!"

    high_gas_alert = " 🚨 High gas levels detected!"

    abnormal_light_alert = " 🚨 Abnormal light levels!"





    #Alerts
    if current_temperature < MIN_TEMP:
        custom_warning(low_temp_alert) 
        send_email("Low Temprature Alert", low_temp_msg)          

    if current_temperature > MAX_TEMP:
        custom_warning(high_temp_alert)  
        send_email("High Temprature Alert", high_temp_msg)  

    if current_humidity < MIN_HUMID:
        custom_warning(low_humid_alert)  
        send_email("Low Humidity Alert", low_humidity_msg)     

    if current_humidity > MAX_HUMID:
        custom_warning(high_humid_alert)
        send_email("High Humidity Alert", high_humidity_msg)  
        

    if current_gas > GAS_THRESHOLD:
        custom_warning(high_gas_alert)
        send_email("High Gas Level Alert", high_gas_msg)  
    
        

    if current_light > LIGHT_THRESHOLD:  
        custom_warning(abnormal_light_alert)
        send_email("Abnormal light alert", abnormal_light_msg)     
       
        
    # Display indoor data in a table
    message = "Indoor Monitoring"
    st.markdown(f'<div style="padding:8px;"><p style="color:black; font-size:20px; font:bold;"> {message}</p></div>', unsafe_allow_html=True)
    st.table([indoor_data])

    
    # Icons for different metrics
    temperature_icon = "🌡️"
    humidity_icon = "💧"
    gas_icon = "⛽"
    light_icon = "💡"
    time_icon = "⏰"

 
    display_weather_data()
    



    
    # Check there is data and plot the graphs
    if filtered_df.empty: 
        st.warning("No data for selected date")
        return
    else:
        # Temperature 
        fig_temp = px.line(filtered_df, x='time', y='temprature')
        fig_temp.update_layout(
            title=f"{temperature_icon} Temperature", 
            font=dict(size=18),
            title_x=0.49,
            xaxis=dict(
                title="Time",
                titlefont=dict(size=16, family='Arial', color='black'),  # Change font size, family, and color for x-axis title
                tickfont=dict(size=14, family='Arial', color='black'),    # Change font size, family, and color for x-axis ticks
                tickformat='%H:%M:%S'  # Set the format to display only time (hours:minutes:seconds)

            ),
            yaxis=dict(
                title="Temperature (C)",
                titlefont=dict(size=16, family='Arial', color='black'),  # Change font size, family, and color for y-axis title
                tickfont=dict(size=14, family='Arial', color='black'),    # Change font size, family, and color for y-axis ticks
        
            ),
        )
        st.plotly_chart(fig_temp)

        # Humidity
        fig_hum = px.line(filtered_df, x='time', y='humidity')
        fig_hum.update_layout(
            title=f"{humidity_icon} Humidity", 
            font=dict(size=18),
            title_x=0.49,
            xaxis=dict(
                title="Time",
                titlefont=dict(size=16, family='Arial', color='black'),  # Change font size, family, and color for x-axis title
                tickfont=dict(size=14, family='Arial', color='black'),    # Change font size, family, and color for x-axis ticks
                tickformat='%H:%M:%S'  # Set the format to display only time (hours:minutes:seconds)

            ),
            yaxis=dict(
                title="Humidity (%)",
                titlefont=dict(size=16, family='Arial', color='black'),  # Change font size, family, and color for y-axis title
                tickfont=dict(size=14, family='Arial', color='black'),    # Change font size, family, and color for y-axis ticks

            ),
        )
        st.plotly_chart(fig_hum)

        # Gas 
        fig_gas = px.line(filtered_df, x='time', y='gas')
        fig_gas.update_layout(
            title=f"{gas_icon} Gas", 
            font=dict(size=18),
            title_x=0.49,
            xaxis=dict(
                title="Time",
                titlefont=dict(size=16, family='Arial', color='black'),  # Change font size, family, and color for x-axis title
                tickfont=dict(size=14, family='Arial', color='black'),    # Change font size, family, and color for x-axis ticks
                tickformat='%H:%M:%S'  # Set the format to display only time (hours:minutes:seconds)

            ),
            yaxis=dict(
                title="Gas (units)",
                titlefont=dict(size=16, family='Arial', color='black'),  # Change font size, family, and color for y-axis title
                tickfont=dict(size=14, family='Arial', color='black'),    # Change font size, family, and color for y-axis ticks
            
            ),
        )
        st.plotly_chart(fig_gas)

        # Light
        fig_light = px.line(filtered_df, x='time', y='light')
        fig_light.update_layout(
            title=f"{light_icon} Light", 
            font=dict(size=18),
            title_x=0.49,
            xaxis=dict(
                title="Time",
                titlefont=dict(size=16, family='Arial', color='black'),  # Change font size, family, and color for x-axis title
                tickfont=dict(size=14, family='Arial', color='black'),    # Change font size, family, and color for x-axis ticks
                tickformat='%H:%M:%S'  # Set the format to display only time (hours:minutes:seconds)

            ),
            yaxis=dict(
                title="Light (units)",
                titlefont=dict(size=16, family='Arial', color='black'),  # Change font size, family, and color for y-axis title
                tickfont=dict(size=14, family='Arial', color='black'),    # Change font size, family, and color for y-axis ticks

            ),
        )
        st.plotly_chart(fig_light)
        


# data        
df = load_data()


#check whether data is available on specific date
def validate_date(date):
    return date in df['time'].dt.date.unique()

# Function to display dashboard
def display_dashboard():

    # Add image to the sidebar
    st.sidebar.image("logo Background Removed.png")

    if df is not None:
        min_date = df['time'].min().date()
        max_date = df['time'].max().date()

        # Set today's date as default within the allowed range
        default_date = datetime.now().date()
        if default_date < min_date:
            default_date = min_date
        elif default_date > max_date:
            default_date = max_date

        # Date input widget with custom validation function
        selected_date = st.sidebar.date_input(
            'Select Date',
            min_value=min_date,
            max_value=max_date,
            value=default_date,
            key='date_input',
            help="Please select a date.",
            )
        
        # Validate selected date
        if not validate_date(selected_date):
            st.error("No data available for the selected date. We will show the last date graphs in our calendar!")
            selected_date = max_date  # Reset date to minimum available date

        if st.sidebar.download_button(label="Download CSV", data=df.to_csv(index=False), file_name='data.csv', mime='text/csv'):
            pass 
    
        plot_charts(df, selected_date)
       
    else:
        st.error("Unable to retrieve data")





 

if __name__ == '__main__':

    display_dashboard()
    # Refresh after 600 seconds (10 minutes)
    while True:
        time.sleep(6*10)
        st.experimental_rerun()
