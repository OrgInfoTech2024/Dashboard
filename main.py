from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from language import languageDictionary
import os
import sys
import requests

API_KEY = 'c0d549ee75209d8ee82a821d1fd77d5b'
CITY_NAME = ''

NEWS_API_KEY = '3fe163b9e2d44cb08ed2dc48578f1c52'
NEWS_API_ENDPOINT = 'https://newsapi.org/v2/top-headlines'
NEWS_API_PARAMS = {'country': 'ua', 'apiKey': NEWS_API_KEY}


class CurrencyConverter:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://open.er-api.com/v6/latest/"

    def convert(self, from_currency, to_currency, amount):
        url = f"{self.base_url}{from_currency.upper()}"
        response = requests.get(url)
        if response.status_code != 200:
            return "Failed to fetch exchange rates."
        data = response.json()
        if to_currency.upper() not in data["rates"]:
            return "Invalid currency."
        exchange_rate = data["rates"][to_currency.upper()]
        converted_amount = amount * exchange_rate
        return converted_amount


class News(QWidget):
    def __init__(self):
        super().__init__()
        self.converter = CurrencyConverter(API_KEY)

        self.saved_list = []

        # MAIN
        self.setWindowTitle(self.tr("News"))
        self.setMinimumSize(600, 400)
        self.setWindowIcon(QIcon("icon.png"))
        
        self.lang = languageDictionary
        self.syslang = QLocale.system().name()
        if self.syslang not in self.lang:
            self.syslang = "en_US"

        # "WEATHER" LABEL
        self.weather_label = QLabel(self.lang[self.syslang]["Weather:"], self)
        self.weather_label.setGeometry(5, 5, 210, 25)

        # "COMMUNITY" INPUT
        self.community_input = QLineEdit(self)
        self.community_input.setPlaceholderText(self.lang[self.syslang]["Your community"])
        self.community_input.setGeometry(5, 30, 210, 25)

        # "FIND" BUTTON
        self.find_button = QPushButton(self.lang[self.syslang]["Find"], self)
        self.find_button.setGeometry(5, 60, 210, 35)
        self.find_button.clicked.connect(self.find)

        # "SAVED" LISTBOX
        self.saved_listbox = QListWidget(self)
        self.saved_listbox.setGeometry(5, 100, 210, 50)
        self.saved_listbox.itemClicked.connect(self.item_clicked)

        # "ADD" BUTTON
        self.add_button = QPushButton(self.lang[self.syslang]["Add"], self)
        self.add_button.setGeometry(5, 155, 100, 35)
        self.add_button.clicked.connect(self.add)

        # "REMOVE" BUTTON
        self.remove_button = QPushButton("Remove", self)
        self.remove_button.setGeometry(110, 155, 105, 35)
        self.remove_button.clicked.connect(self.remove)

        # "CURRENCY" LABEL
        self.currency_label = QLabel(self.lang[self.syslang]["Currency:"], self)
        self.currency_label.setGeometry(5, 195, 210, 25)

        # "MONEY" INPUT
        self.money_input = QLineEdit(self)
        self.money_input.setPlaceholderText(self.lang[self.syslang]["Your money"])
        self.money_input.setGeometry(5, 232, 140, 25)

        # "YOUR CURRENCY" COMBOBOX
        self.your_currency_combobox = QComboBox(self)
        self.your_currency_combobox.setGeometry(150, 215, 65, 30)
        self.your_currency_combobox.addItems(['AED', 'AMD', 'AZN', 'CAD', 'CNY', 'EUR', 'FRF', 'GBP', 'GEL', 'JPY', 'KRW', 'KZT', 'MDL', 'PLN', 'TMT', 'TRY', 'UAH', 'USD'])

        # "CURRENCY" LABEL
        self.result_label = QLabel(self.lang[self.syslang]["Result: "], self)
        self.result_label.setGeometry(5, 275, 210, 25)

        # "TRANSLATE CURRENCY" COMBOBOX
        self.translate_currency_combobox = QComboBox(self)
        self.translate_currency_combobox.setGeometry(150, 240, 65, 30)
        self.translate_currency_combobox.addItems(['AED', 'AMD', 'AZN', 'CAD', 'CNY', 'EUR', 'FRF', 'GBP', 'GEL', 'JPY', 'KRW', 'KZT', 'MDL', 'PLN', 'TMT', 'TRY', 'UAH', 'USD'])

        # "TRANSLATE" BUTTON
        self.translate_button = QPushButton(self.lang[self.syslang]["Translate"], self)
        self.translate_button.setGeometry(5, 300, 210, 35)
        self.translate_button.clicked.connect(self.translate)

        # "ABOUT" BUTTON
        self.about_button = QPushButton(self.lang[self.syslang]["About"], self)
        self.about_button.setGeometry(5, 340, 210, 35)
        self.about_button.clicked.connect(self.about)


        # "ABOUT" LABEL
        
        about = self.lang[self.syslang]["News\nVersion: 1.0.0\nCompany: OrgInfoTech"]

        self.about_label = QLabel(about, self)
        self.about_label.setGeometry(250, 30, 190, 100)
        self.about_label.hide()

        # "NEWS" WEBBROWSER
        self.webBrowserNews = QWebEngineView(self)
        self.webBrowserNews.setUrl(QUrl('https://www.ukr.net'))
        self.webBrowserNews.setGeometry(220, 5, 370, 390)

        # "WEATHER TODAY" LABEL
        self.weather_today_label = QLabel(self.lang[self.syslang]["Weather today: "], self)
        self.weather_today_label.setGeometry(250, 30, 190, 120)
        self.weather_today_label.hide()

        # "WEATHER TOMORROW" LABEL
        self.weather_tomorrow_label = QLabel(self.lang[self.syslang]["Weather tomorrow: "], self)
        self.weather_tomorrow_label.setGeometry(250, 155, 190, 100)
        self.weather_tomorrow_label.hide()

        # "GO TO NEWS" BUTTON
        self.go_to_button = QPushButton(self.lang[self.syslang]["Go to news"], self)
        self.go_to_button.clicked.connect(self.go_to)
        self.go_to_button.setGeometry(250, 300, 210, 35)
        self.go_to_button.hide()

        self.load_saved_list()
        self.resizeEvent = self.on_resize

    
    # "FIND" FUNCTION

    def find(self):
        # HIDE
        self.about_label.hide()
        self.webBrowserNews.hide()

        # SHOW
        self.weather_today_label.show()
        self.weather_tomorrow_label.show()
        self.go_to_button.show()
        
        CITY_NAME = self.community_input.text()
        url = f'https://api.openweathermap.org/data/2.5/weather?q={CITY_NAME}&appid={API_KEY}&units=metric'
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()

            # Today's weather
            today_weather = data['weather'][0]['description']
            today_clouds = data['clouds']['all']
            today_pressure = data['main']['pressure']
            today_visibility = data['visibility']
            today_temp_min = data['main']['temp_min']
            today_temp_max = data['main']['temp_max']

            self.weather_today_label.setText(
                self.lang[self.syslang]["In community"] + f": {CITY_NAME}:\n" +
                self.lang[self.syslang]["Today"] + f": {today_weather}\n" +
                self.lang[self.syslang]["Clouds"] + f": {today_clouds}%\n" +
                self.lang[self.syslang]["Pressure"] + f": {today_pressure} mm\n" +
                self.lang[self.syslang]["Visibility"] + f": {int(today_visibility) // 1000} km\n" +
                self.lang[self.syslang]["Temperature (Minimum)"] + f":  {today_temp_min}°C\n" +
                self.lang[self.syslang]["Temperature (Maximum)"] + f":  {today_temp_max}°C"
            )

            # Tomorrow's weather
            url = f'https://api.openweathermap.org/data/2.5/forecast?q={CITY_NAME}&appid={API_KEY}&units=metric'
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()

                tomorrow_weather = data['list'][8]['weather'][0]['description']
                tomorrow_clouds = data['list'][8]['clouds']['all']
                tomorrow_pressure = data['list'][8]['main']['pressure']
                tomorrow_visibility = data['list'][8]['visibility']
                tomorrow_temp_min = data['list'][8]['main']['temp_min']
                tomorrow_temp_max = data['list'][8]['main']['temp_max']

                self.weather_tomorrow_label.setText(
                    self.lang[self.syslang]["Tomorrow"] + f": {tomorrow_weather}\n" +
                    self.lang[self.syslang]["Clouds"] + f": {tomorrow_clouds}%\n" +
                    self.lang[self.syslang]["Pressure"] + f": {tomorrow_pressure} mm\n" +
                    self.lang[self.syslang]["Visibility"] + f": {int(tomorrow_visibility) // 1000} km\n" +
                    self.lang[self.syslang]["Temperature (Minimum)"] + f": {tomorrow_temp_min}°C\n" +
                    self.lang[self.syslang]["Temperature (Maximum)"] + f": {tomorrow_temp_max}°C"
                )

    
    # LOAD SAVED LIST

    def load_saved_list(self):
        try:
            # Get the home directory of the current user
            home_directory = os.path.expanduser("~")
            
            # Construct the full file path
            file_path = os.path.join(home_directory, '.programdates', 'weather.txt')

            with open(file_path, 'r') as f:
                self.saved_list = [line.strip() for line in f.readlines()]
                self.saved_listbox.addItems(self.saved_list)
        except FileNotFoundError:
            pass


    # CLOSING OF PROGRAMM
    
    def closeEvent(self, event):
        # Get the home directory of the current user
        home_directory = os.path.expanduser("~")
            
        # Construct the full file path
        file_path = os.path.join(home_directory, '.programdates', 'weather.txt')

        with open(file_path, 'w') as f:
            for item in self.saved_list:
                f.write(f'{item}\n')
        event.accept()


    # "ITEM CLICKED" FUNCTION

    def item_clicked(self, item):
            selected_text = item.text()
            self.community_input.setText(selected_text)
            self.find()

    
    # "ADD" FUNCTION

    def add(self):
        text = self.community_input.text()
        self.saved_list.append(str(text))
        self.saved_listbox.clear()
        self.saved_listbox.addItems(self.saved_list)
    

    # "REMOVE" FUNCTION

    def remove(self):
        selected_item = self.saved_listbox.currentItem()
        if selected_item:
            text = selected_item.text()
            self.saved_list.remove(text)
            self.saved_listbox.clear()
            self.saved_listbox.addItems(self.saved_list)
    

    # "TRANSLATE" FUNCTION

    def translate(self):
        from_currency = self.your_currency_combobox.currentText()
        to_currency = self.translate_currency_combobox.currentText()
        amount = float(self.money_input.text())
        converted_amount = self.converter.convert(from_currency, to_currency, amount)
        if isinstance(converted_amount, str):
            self.result_label.setText(converted_amount)
        else:
            self.result_label.setText(f"Converted amount: {converted_amount:.2f} {to_currency}")

        # Clear input fields after conversion
        self.money_input.clear()
    

    # "ABOUT" FUNCTION

    def about(self):
        # HIDE
        self.weather_today_label.hide()
        self.weather_tomorrow_label.hide()
        self.news_label.hide()

        # SHOW
        self.go_to_button.show()
        self.about_label.show()
    

    # "GO TO NEWS" FUNCTION

    def go_to(self):
        # HIDE
        self.weather_today_label.hide()
        self.weather_tomorrow_label.hide()
        self.go_to_button.hide()
        self.about_label.hide()

        # SHOW
        self.webBrowserNews.show()

    # Function to handle resizing event
    def on_resize(self, event):
        # Adjust the size and position of the webBrowserNews when the main window is resized
        new_size = event.size()
        self.webBrowserNews.setGeometry(220, 5, new_size.width() - 230, new_size.height() - 10)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    welcome_window = News()
    welcome_window.show()
    sys.exit(app.exec_())