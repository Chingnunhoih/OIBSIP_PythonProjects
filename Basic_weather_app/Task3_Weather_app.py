import requests

# -------------------------------
# Basic Weather App (Python)
# -------------------------------
# This app retrieves weather data for a user-entered city
# and displays temperature, humidity, and conditions.
# -------------------------------

API_KEY = "37802d0e200aac1dacfae5182ef65d0f"  # Replace with your OpenWeatherMap API key

def get_weather(city):
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"  # Celsius
    }
    
    try:
        response = requests.get(base_url, params=params)
        data = response.json()

        # Check if the city exists
        if data["cod"] != 200:
            print("\n❌ Error:", data.get("message", "Unknown error"))
            return

        # Extract important info
        temperature = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        condition = data["weather"][0]["description"]

        print("\n====== Weather Information ======")
        print(f"City: {city.title()}")
        print(f"Temperature: {temperature}°C")
        print(f"Humidity: {humidity}%")
        print(f"Condition: {condition}")
        print("================================")

    except requests.exceptions.RequestException:
        print("\n❌ Network error: Unable to retrieve weather data.")


# ------------- MAIN PROGRAM -------------
while True:
    city = input("\nEnter a city name (or 'exit' to quit): ").strip()

    if city.lower() == "exit":
        print("Goodbye!")
        break

    if city == "":
        print("Please enter a valid city name.")
        continue

    get_weather(city)
