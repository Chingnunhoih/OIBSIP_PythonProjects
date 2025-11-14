Basic Weather App (Python)

Description:

This is a beginner-friendly command-line weather application built using
Python. It retrieves real-time weather data for any user-specified city
using the OpenWeatherMap API. The program displays essential weather
details such as:

-   Temperature (°C)
-   Humidity (%)
-   Weather conditions (e.g., clear sky, rain, fog)

Features:

-   Fetches live weather data from an online API
-   Accepts user input for the city name
-   Provides error handling for invalid city names or network issues
-   Simple and easy-to-understand Python code
-   Continuous loop to check multiple cities until the user types “exit”

Requirements:

1.  Python installed on your system
2.  Install the ‘requests’ library: pip install requests
3.  An OpenWeatherMap API key (free)
    Create an account at: https://openweathermap.org/

How to Use:

1.  Replace the API_KEY variable in the script with your own key.
2.  Run the script in a terminal or command prompt: python
    weather_app.py
3.  When prompted, enter the name of any city.
4.  Type “exit” anytime to close the program.

Code Overview:

-   The program uses requests.get() to send API requests.
-   Weather information is retrieved in JSON format.
-   Extracted fields:
    -   data[“main”][“temp”]
    -   data[“main”][“humidity”]
    -   data[“weather”][0][“description”]
-   The program validates user input and handles incorrect API
    responses.

Notes:

-   Ensure your API key is active (may take up to 10 minutes after
    creation).
-   Internet connection is required for API calls.
