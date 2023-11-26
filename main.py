import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext
import webbrowser
import requests
from datetime import datetime
import time
import geocoder

# Custom method for creating a rounded rectangle on a canvas
def create_rounded_rectangle(self, x1, y1, x2, y2, radius, **kwargs):
    points = [x1 + radius, y1,
              x1 + radius, y1,
              x2 - radius, y1,
              x2 - radius, y1,
              x2, y1,
              x2, y1 + radius,
              x2, y1 + radius,
              x2, y2 - radius,
              x2, y2 - radius,
              x2, y2,
              x2 - radius, y2,
              x2 - radius, y2,
              x1 + radius, y2,
              x1 + radius, y2,
              x1, y2,
              x1, y2 - radius,
              x1, y2 - radius,
              x1, y1 + radius,
              x1, y1 + radius,
              x1, y1]

    return self.create_polygon(points, **kwargs)

# Attach the custom method to the Canvas class
tk.Canvas.create_rounded_rectangle = create_rounded_rectangle

def get_api_key():
    # Prompt the user for their OpenWeatherMap API key
    api_key = simpledialog.askstring("API Key", "Enter your OpenWeatherMap API key:\n(If you don't have one, get it from https://openweathermap.org/api)")
    return api_key

def check_api_key():
    while True:
        try:
            with open("api_key.txt", "r") as f:
                api_key = f.read().strip()
                if not api_key:
                    raise FileNotFoundError
            break  # Break out of the loop if a valid key is found
        except FileNotFoundError:
            # If the file doesn't exist or the key is empty, prompt the user for the API key
            api_key = get_api_key()
            # Save the user's API key to the script
            with open("api_key.txt", "w") as f:
                f.write(api_key)
    return api_key

def change_api_key():
    # Change the API key and save it to the script
    api_key = get_api_key()
    with open("api_key.txt", "w") as f:
        f.write(api_key)

def open_api_documentation():
    # Open the OpenWeatherMap API documentation in the default web browser
    webbrowser.open("https://openweathermap.org/api")

def change_units():
    # Change the units for temperature and save the preference
    units = simpledialog.askstring("Units", "Enter preferred units for temperature (e.g., metric, imperial):").strip().lower()
    with open("units.txt", "w") as f:
        f.write(units)

def get_forecast():
    # Check if the API key is set
    api_key = check_api_key()

    city = selected_city.get()

    # If the selected city is "Current Location", use geocoder to get the current location
    if city == "Current Location":
        try:
            location = geocoder.ip('me')
            city = location.city
        except:
            show_error_message("Unable to determine your current location.")
            return

    base_url = "http://api.openweathermap.org/data/2.5/forecast"
    params = {"q": city, "appid": api_key, "units": "metric"}

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
        data = response.json()

        if data["cod"] == "404":
            # City not found
            error_message = f"City '{city}' not found. Please enter a valid city name."
            show_error_message(error_message)
            return

        # Extract relevant information from the response
        forecasts = data["list"][:8]  # Get the first 8 forecasts (next 3 days, 3-hour intervals)

        forecast_text = ""
        for forecast in forecasts:
            timestamp = forecast["dt"]
            date = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            temperature = forecast["main"]["temp"]
            description = forecast["weather"][0]["description"]

            forecast_text += f"Date: {date}\nTemperature: {temperature}°C\nDescription: {description}\n\n"

        # Update the GUI with the weather forecast information
        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, forecast_text)
        result_text.config(state=tk.DISABLED)

    except requests.exceptions.RequestException as e:
        # Handle API request errors
        error_message = f"API request error: {e}"
        show_error_message(error_message)

    except requests.exceptions.HTTPError as e:
        # Handle HTTP errors (4xx or 5xx)
        error_message = f"HTTP error: {e}"
        show_error_message(error_message)

    except KeyError:
        # Handle the case where there's an issue with the API response
        error_message = "Invalid API response format."
        show_error_message(error_message)

def update_time():
    current_time = time.strftime("%H:%M:%S")
    time_label.config(text=f"Current Time: {current_time}")
    app.after(1000, update_time)  # Update every 1000 milliseconds (1 second)

def get_weather(*args):
    # Check if the API key is set
    api_key = check_api_key()

    city = selected_city.get()

    # If the selected city is "Current Location", use geocoder to get the current location
    if city == "Current Location":
        try:
            location = geocoder.ip('me')
            city = location.city
        except:
            show_error_message("Unable to determine your current location.")
            return

    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": api_key, "units": "metric"}

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
        data = response.json()

        if data["cod"] == "404":
            # City not found
            error_message = f"City '{city}' not found. Please enter a valid city name."
            show_error_message(error_message)
            return

        # Extract relevant information from the response
        temperature = data["main"]["temp"]
        description = data["weather"][0]["description"]
        city_name = data["name"]

        # Determine the time of the day
        current_time = datetime.utcnow().hour
        time_of_day = "Morning" if 6 <= current_time < 12 else "Afternoon" if 12 <= current_time < 18 else "Night"

        # Update the GUI with the weather information
        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, f"City: {city_name}\nTemperature: {temperature}°C\nDescription: {description}\nTime of Day: {time_of_day}")
        result_text.config(state=tk.DISABLED)

    except requests.exceptions.RequestException as e:
        # Handle API request errors
        error_message = f"API request error: {e}"
        show_error_message(error_message)

    except requests.exceptions.HTTPError as e:
        # Handle HTTP errors (4xx or 5xx)
        error_message = f"HTTP error: {e}"
        show_error_message(error_message)

    except KeyError:
        # Handle the case where there's an issue with the API response
        error_message = "Invalid API response format."
        show_error_message(error_message)

def show_error_message(message):
    messagebox.showerror("Error", message)

def exit_app():
    app.destroy()

# Create the main application window
app = tk.Tk()
app.title("Worldwide Weather App")

# Set window size and center it on the screen
window_width = 400
window_height = 600
screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()
x_position = (screen_width - window_width) // 2
y_position = (screen_height - window_height) // 2
app.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

# Set window background color
app.configure(bg="#34495e")  # Background color

# Adding a border
app.tk_setPalette(background="#34495e", foreground="#ecf0f1")  # Background and foreground colors

# Create a menu bar
menu_bar = tk.Menu(app, bg="#2c3e50", fg="#ecf0f1")  # Menu bar color
app.config(menu=menu_bar)

# Create the File menu
file_menu = tk.Menu(menu_bar, tearoff=0, bg="#2c3e50", fg="#ecf0f1")  # File menu color
menu_bar.add_cascade(label="File", menu=file_menu)

# Add an option to exit the application
file_menu.add_command(label="Exit", command=exit_app)

# Create the Settings menu
settings_menu = tk.Menu(menu_bar, tearoff=0, bg="#2c3e50", fg="#ecf0f1")  # Settings menu color
menu_bar.add_cascade(label="Settings", menu=settings_menu)

# Add options to change the API key, units, and view the API documentation
settings_menu.add_command(label="Change API Key", command=change_api_key)
settings_menu.add_command(label="Change Units", command=change_units)

# Create the API menu
api_menu = tk.Menu(menu_bar, tearoff=0, bg="#2c3e50", fg="#ecf0f1")  # API menu color
menu_bar.add_cascade(label="API", menu=api_menu)

# Add options to change the API key and view the API documentation
api_menu.add_command(label="Change API Key", command=change_api_key)
api_menu.add_command(label="View API Documentation", command=open_api_documentation)

# List of countries in the world
world_cities = ["Current Location", "New York", "London", "Tokyo", "Paris", "Berlin", "Beijing", "Sydney", "Moscow", "Rio de Janeiro","kenya"]

# Create a dropdown menu with the world cities
selected_city = tk.StringVar()
city_label = tk.Label(app, text="Select city:", font=("Helvetica", 14), bg="#34495e", fg="#ecf0f1")
city_label.pack(pady=10)

city_dropdown_values = world_cities
city_dropdown = ttk.Combobox(app, textvariable=selected_city, values=city_dropdown_values, font=("Helvetica", 14))
city_dropdown.pack(pady=10)

# Set a default city
city_dropdown.set(city_dropdown_values[0])

# Add an event handler to the dropdown to trigger get_weather when the selection changes
city_dropdown.bind("<<ComboboxSelected>>", get_weather)

# Create a button to get the weather
get_weather_button = tk.Button(app, text="Get Weather", command=get_weather, font=("Helvetica", 14), bg="#3498db", fg="white", bd=2)
get_weather_button.pack(pady=15)

# Create a button to get the weather forecast
get_forecast_button = tk.Button(
    app, text="Get Weather Forecast", command=get_forecast, font=("Helvetica", 14), bg="#2ecc71", fg="white", bd=2
)
get_forecast_button.pack(pady=15)

# Creating a canvas for the rounded rectangle
canvas = tk.Canvas(app, width=350, height=200, bg="#34495e", highlightthickness=0)
canvas.pack(pady=20)

# Creating a rounded rectangle on the canvas
rounded_rectangle = canvas.create_rounded_rectangle(0, 0, 350, 200, radius=20, fill="#2c3e50", outline="#2c3e50")

# Creating a frame for better organization
result_frame = tk.Frame(canvas, bg="#2c3e50")
result_frame.place(relx=0.8, rely=0.7, anchor="center")

# Creating a scrolled text widget for displaying the weather information
result_text = scrolledtext.ScrolledText(
    result_frame, wrap=tk.WORD, width=45, height=10, font=("Arial", 12, "bold"), bg="#2c3e50", fg="#ecf0f1", bd=0, relief="flat"
)
result_text.pack(expand=True, fill=tk.BOTH)

# Configure the scroll bar to scroll the result
scroll_bar = ttk.Scrollbar(result_frame, command=result_text.yview)
scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)
result_text.config(yscrollcommand=scroll_bar.set)

# Creating a label for displaying the current time
time_label = tk.Label(app, text="", font=("Helvetica", 14), bg="#34495e", fg="#ecf0f1")
time_label.pack()

# Adding a footer with contact information and version
footer_label = tk.Label(app, text="App created by Thiarara\nContact: contact@thiarara.co.ke\n \n Version 1.5", font=("Calibri", 9), bg="#34495e", fg="#E6E6FA")
footer_label.pack(pady=10)

# Start updating the time
update_time()

# Start the Tkinter event loop
app.mainloop()
