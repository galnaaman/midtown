import streamlit as st
import requests
import logging
import sqlite3
from datetime import datetime
import pandas as pd

st.set_page_config(
    page_title="Midtown Tracker",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded", )
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)
# Replace 'your_bot_token' and 'your_chat_id' with your actual values
bot_token = '6671561034:AAE-I-eUsf81XsIBup_wVzpn7wbRecEMAnk'
chat_id = '729712388'

# Sample family members

family_members = [
    "שגיב שרעבי",
    "מאור פבריקנט",
    "גל נעמן",
    "עומר יששכרוב",
    "עדי קומרז",
    "אלדד ברגר",
    "יותם וירניק",
    "שרון דניאלי",
    "מעיין אוחיון",
    "שירה גולדפרב",
    "אושר אברהם",
    "דניאל גויכמן",
    "תמי מזרחי",
    "עמית איובי",
    "יובל רוזנמן"
]

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('locations.db')
c = conn.cursor()

# Create table if it doesn't exist
c.execute('''
    CREATE TABLE IF NOT EXISTS locations (
        name TEXT,
        place TEXT,
        date TEXT
    )
''')


def create_location(name, place):
    current_date = datetime.now().strftime('%d-%b-%y')
    c.execute("INSERT INTO locations VALUES (?, ?, ?)", (name, place, current_date))
    conn.commit()


def read_locations():
    c.execute("SELECT * FROM locations ORDER BY name")
    rows = c.fetchall()
    logging.error(f"Rows: {rows}")
    locations = []
    # Rows: [('gal', 'Home', '05-Nov-23')]
    for i in range(len(rows)):
        member = {
            "name": rows[i][0],
            "place": rows[i][1],
            "date": rows[i][2]
        }
        locations.append(member)

    logging.info(f"Locations: {locations}")
    return locations


def update_location(name, new_place):
    current_date = datetime.now().strftime('%d-%b-%y')
    c.execute("UPDATE locations SET place = ?, date = ? WHERE name = ?", (new_place, current_date, name))
    conn.commit()


def delete_location(name):
    c.execute("DELETE FROM locations WHERE name = ?", (name,))
    conn.commit()


def is_updated_today(name):
    current_date = datetime.now().strftime('%d-%b-%y')
    c.execute("SELECT date FROM locations WHERE name = ?", (name,))
    result = c.fetchone()
    if result is None:
        return False
    else:
        return result[0] == current_date


def clear():
    c.execute("DELETE FROM locations")
    conn.commit()


def check():
    for member in family_members:
        if not is_updated_today(member):
            return False
    return True


def send_telegram_message():
    locations = read_locations()
    current_date = datetime.now().strftime("%H:%M - %d/%m/%Y")
    message = f"דוח 1 לבוקר זה {current_date}  !\n\n"
    for member in locations:
        index = locations.index(member) + 1
        message += f"{index}. {member['name']}  {member['place']}\n"
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={message}"
    logging.info(f"Sending message to Telegram API: {url}")
    request = requests.post(url)
    logging.info(f"Telegram API's response: {request.json()}")


def display_locations():
    c.execute("SELECT * FROM locations ORDER BY name")
    rows = c.fetchall()
    locations = rows
    logging.debug(f"Locations: {locations}")
    df = pd.DataFrame(locations, columns=["Name", "Place", "Date"])
    st.table(df)


# Navigation sidebar
page = st.sidebar.selectbox("Choose a page", ["Home", "Locations"])

if page == "Home":
    st.title("Midtown 🏙️ Location Tracker")
    st.write("Welcome to the Midtown location tracker!״")
    st.write("בעקבות קבלת הסיבוס אנחנו נדרשים לשלוח הודעה לבית אסיה עד 9:30 , נא לעדכן את מיקומכם כאן כדי שנוכל לדעת "
             "מי נמצא בבית ומי נמצא ביחידה. על מנת שנוכל להמשיך להנות מהסיבוס")

    name = st.selectbox("Select your name:", family_members)
    location = st.selectbox("Select your location:", ["בבית", "נוכח ביחידה "])

    if st.button("Submit"):
        if is_updated_today(name):
            st.warning("You already updated your location today!")
        else:
            create_location(name, location)
            logging.info(f"Location of {name} was updated to {location}.")
            st.success("Your location was successfully updated!")
        if check():
            st.info("All family members updated their location today!")
            send_telegram_message()
            clear()


elif page == "Locations":
    display_locations()
