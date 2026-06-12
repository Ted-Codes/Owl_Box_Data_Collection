import cv2
import yt_dlp
import os
from google import genai
from PIL import Image
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import requests

#----------------------------------#
#GET TIME
#----------------------------------#

timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#----------------------------------#
#GET WEATHER
#----------------------------------#

def get_weather(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    data = requests.get(url).json()

    temp = data["current_weather"]["temperature"]
    code = data["current_weather"]["weathercode"]

    weather_map = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        61: "Rain",
        80: "Rain showers",
    }

    temperature_string = f"{temp}°C"
    weather_string = weather_map.get(code, "Unknown")

    return weather_string, temperature_string

sycamore_weather, sycamore_temp = get_weather(37.7022, -121.9358)

#----------------------------------#
#YOUTUBE PULL
#----------------------------------#

YOUTUBE_URL = "https://www.youtube.com/watch?v=CtDX8msDCQs"

# Get direct stream URL
ydl_opts = {
    "quiet": True,
    "format": "best"
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(YOUTUBE_URL, download=False)
    stream_url = info["url"]

# Open stream
cap = cv2.VideoCapture(stream_url)

ret, frame = cap.read()

if ret:
    cv2.imwrite("current_frame.jpg", frame)
else:
    pass

cap.release()

#----------------------------------#
# Detect Owls
#----------------------------------#

# Create client
client = genai.Client(
    api_key="os.environ["API_KEY"]
)

# Load image
image = Image.open("current_frame.jpg")

# Ask Gemini to count owls
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[
        image,
        """
        Count the owls visible in this owl-box image.

        Rules:
        - Count only actual owls.
        - Return only a single integer.
        - Do not provide any explanation.
        """
    ]
)

# # SHOW PICTURE
# cv2.imshow("Current Frame", frame)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

#----------------------------------#
# SAVE TO GOOGLE SHEETS
#----------------------------------#

FORM_URL = ("https://docs.google.com/forms/d/e/1FAIpQLSfZ7w19yEUymHa3MgLenT9PT8Kq411iAECfv28-"
            "Ni7Z_T06HQ/formResponse")

requests.post(
    FORM_URL,
    data={
        "entry.100495192": timestamp,
        "entry.309741449": response.text,
        "entry.288743641": sycamore_temp,
        "entry.404478198": sycamore_weather,
    }
)
