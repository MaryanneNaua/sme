import requests
import json
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image as KivyImage
from kivy.uix.screenmanager import ScreenManager, Screen
from datetime import datetime, timedelta
from kivy.graphics import Color, Ellipse, Rectangle, RoundedRectangle

FIREBASE_URL = "https://test-2f068-default-rtdb.firebaseio.com/"  # Replace with your Firebase project URL
API_KEY = "AIzaSyCBYnzLZvWtCvUKBIhN-az5iOJKMOb17-U"  # Replace with your Firebase API key


class UserApp(Screen):
    def __init__(self, **kwargs):
        super(UserApp, self).__init__(**kwargs)
        layout = FloatLayout()

        # Background Image
        background = KivyImage(source='background.jpg', allow_stretch=True, keep_ratio=False)
        layout.add_widget(background)

        # Logo Image (adjust the y value for padding)
        logo = KivyImage(source='logo.png', size_hint=(0.2, 0.2), pos_hint={'center_x': 0.5, 'y': 0.8}) # Adjust y for padding
        layout.add_widget(logo)

        # Name Input
        self.name_input = TextInput(hint_text='Enter Your Name', multiline=False, size_hint=(0.8, None), height=40)
        self.name_input.pos_hint = {'x': 0.1, 'y': 0.7}
        layout.add_widget(self.name_input)

        # Email Input
        self.email_input = TextInput(hint_text='Email', multiline=False, size_hint=(0.8, None), height=40)
        self.email_input.pos_hint = {'x': 0.1, 'y': 0.6}
        layout.add_widget(self.email_input)

        # Password Input
        self.password_input = TextInput(hint_text='Password', password=True, multiline=False, size_hint=(0.8, None), height=40)
        self.password_input.pos_hint = {'x': 0.1, 'y': 0.5}
        layout.add_widget(self.password_input)

        # Register Button
        self.register_button = Button(text='Register', size_hint=(0.8, None), height=50)
        self.register_button.pos_hint = {'x': 0.1, 'y': 0.3}
        self.register_button.bind(on_press=self.register_user)
        layout.add_widget(self.register_button)

        # Login Button
        self.login_button = Button(text='Login', size_hint=(0.8, None), height=50)
        self.login_button.pos_hint = {'x': 0.1, 'y': 0.2}
        self.login_button.bind(on_press=self.login_user)
        layout.add_widget(self.login_button)

        self.add_widget(layout)

    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message), size_hint=(0.8, 0.4))
        popup.open()

    def register_user(self, instance):
        name = self.name_input.text
        email = self.email_input.text
        password = self.password_input.text

        if email and password and name:
            url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={API_KEY}"
            data = {
                "email": email,
                "password": password,
                "returnSecureToken": True
            }
            response = requests.post(url, json=data)
            response_data = response.json()

            if response.status_code == 200:
                # Successfully registered, now save the name to Firebase
                user_id = response_data['localId']
                user_details = {
                    "name": name,
                    "email": email,
                }
                # Store user details under the user's UID in Firebase
                requests.put(f"{FIREBASE_URL}/users/{user_id}.json", json=user_details)

                self.show_popup("Success", "User registered successfully!")
                self.email_input.text = ""
                self.password_input.text = ""
                self.name_input.text = ""
            else:
                self.show_popup("Error", response_data.get("error", {}).get("message", "Unknown error occurred."))
        else:
            self.show_popup("Error", "Please fill in all fields.")

    def login_user(self, instance):
        email = self.email_input.text
        password = self.password_input.text

        if email and password:
            url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
            data = {
                "email": email,
                "password": password,
                "returnSecureToken": True
            }
            response = requests.post(url, json=data)
            response_data = response.json()

            if response.status_code == 200:
                self.show_popup("Success", "Logged in successfully!")
                self.email_input.text = ""
                self.password_input.text = ""
                user_id = response_data['localId']  # Save user ID
                self.manager.current = 'dashboard'

                # Store user ID in the Dashboard screen and retrieve name
                dashboard_screen = self.manager.get_screen('dashboard')
                dashboard_screen.user_id = user_id
                dashboard_screen.load_user_name(user_id)  # Load the user name

            else:
                self.show_popup("Error", response_data.get("error", {}).get("message", "Unknown error occurred."))
        else:
            self.show_popup("Error", "Please enter both email and password.")


class DatePickerPopup(Popup):
    def __init__(self, on_date_selected, **kwargs):
        super(DatePickerPopup, self).__init__(**kwargs)
        self.title = "Select a Date"
        self.size_hint = (0.8, 0.8)

        self.on_date_selected = on_date_selected
        self.grid = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.populate_days()

        self.content = BoxLayout(orientation='vertical')
        self.content.add_widget(self.grid)

        btn_close = Button(text='Close', background_color=(0.8, 0.1, 0.1, 1), color=[1, 1, 1, 1])
        btn_close.bind(on_press=self.dismiss)
        self.content.add_widget(btn_close)

    def populate_days(self):
        today = datetime.now()
        start_date = today - timedelta(days=today.weekday())

        for i in range(7):
            day = start_date + timedelta(days=i)
            btn = Button(
                text=day.strftime("%d\n(%a)"),
                background_color=(0.2, 0.6, 0.8, 1),  # Teal button
                color=(1, 1, 1, 1)  # White text
            )
            btn.bind(on_release=lambda instance, selected_day=day: self.date_selected(selected_day))
            self.grid.add_widget(btn)

    def date_selected(self, selected_date):
        self.on_date_selected(selected_date)
        self.dismiss()


class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super(DashboardScreen, self).__init__(**kwargs)
        self.user_id = None
        self.user_name = ""  # To hold user's name
        self.income_records = []
        self.expense_records = []
        self.load_records()

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Welcome Label
        self.welcome_label = Label(text='Welcome!', size_hint_y=None, height=50)
        layout.add_widget(self.welcome_label)

        self.create_income_section(layout)
        self.create_expense_section(layout)

        self.add_widget(layout)

        # Add return and logout buttons
        btn_main_menu = Button(text='Go to Main Menu', size_hint_y=None, height=50)
        btn_main_menu.bind(on_release=self.go_to_main_menu)
        layout.add_widget(btn_main_menu)

        btn_logout = Button(text='Logout', size_hint_y=None, height=50)
        btn_logout.bind(on_release=self.logout)
        layout.add_widget(btn_logout)

    def load_user_name(self, user_id):
        # Load user's name from Firebase
        url = f"{FIREBASE_URL}/users/{user_id}.json"
        response = requests.get(url)
        if response.status_code == 200:
            user_data = response.json()
            self.user_name = user_data.get("name", "User")
            self.welcome_label.text = f'Welcome, {self.user_name}!'  # Update welcome message
        else:
            self.welcome_label.text = "Welcome!"

    def create_income_section(self, layout):
        income_label = Label(text='Enter Income (K):', color=[1, 1, 1, 1])
        layout.add_widget(income_label)

        self.income_input = TextInput(hint_text='Income Amount', multiline=False)
        layout.add_widget(self.income_input)

        self.item_name_income_input = TextInput(hint_text='Item Name', multiline=False)
        layout.add_widget(self.item_name_income_input)

        self.date_input_income = TextInput(hint_text='Select Date (Income)', multiline=False, readonly=True)
        self.date_input_income.bind(on_touch=self.open_date_picker_income)
        layout.add_widget(self.date_input_income)

        self.record_income_button = Button(
            text='Record Income',
            background_color=(0.1, 0.6, 0.1, 1),
            color=[1, 1, 1, 1]
        )
        self.record_income_button.bind(on_release=self.record_income)
        layout.add_widget(self.record_income_button)

    def create_expense_section(self, layout):
        expense_label = Label(text='Enter Expense (K):', color=[1, 1, 1, 1])
        layout.add_widget(expense_label)

        self.expense_input = TextInput(hint_text='Expense Amount', multiline=False)
        layout.add_widget(self.expense_input)

        self.item_name_expense_input = TextInput(hint_text='Item Name', multiline=False)
        layout.add_widget(self.item_name_expense_input)

        self.date_input_expense = TextInput(hint_text='Select Date (Expense)', multiline=False, readonly=True)
        self.date_input_expense.bind(on_touch=self.open_date_picker_expense)
        layout.add_widget(self.date_input_expense)

        self.record_expense_button = Button(
            text='Record Expense',
            background_color=(0.8, 0.1, 0.1, 1),
            color=[1, 1, 1, 1]
        )
        self.record_expense_button.bind(on_release=self.record_expense)
        layout.add_widget(self.record_expense_button)

    def open_date_picker_income(self, instance, touch):
        if instance.collide_point(*touch.pos):  
            popup = DatePickerPopup(on_date_selected=self.set_income_date)
            popup.open()

    def open_date_picker_expense(self, instance, touch):
        if instance.collide_point(*touch.pos):  
            popup = DatePickerPopup(on_date_selected=self.set_expense_date)
            popup.open()

    def set_income_date(self, selected_date):
        self.date_input_income.text = selected_date.strftime("%Y-%m-%d")

    def set_expense_date(self, selected_date):
        self.date_input_expense.text = selected_date.strftime("%Y-%m-%d")

    def record_income(self, instance):
        income_text = self.income_input.text
        item_name = self.item_name_income_input.text
        if income_text and item_name:
            now = datetime.now()
            formatted_datetime = now.strftime("%Y-%m-%d %H:%M:%S")
            record_entry = {
                "amount": f"K{income_text}",
                "item_name": item_name,
                "date": formatted_datetime
            }
            self.income_records.append(record_entry)
            self.income_input.text = ""
            self.item_name_income_input.text = ""
            self.show_info(f"Income recorded: K{income_text} for {item_name} on {formatted_datetime}")
            self.save_records()
        else:
            self.show_error("Please enter the income amount and item name.")

    def record_expense(self, instance):
        expense_text = self.expense_input.text
        item_name = self.item_name_expense_input.text
        if expense_text and item_name:
            now = datetime.now()
            formatted_datetime = now.strftime("%Y-%m-%d %H:%M:%S")
            record_entry = {
                "amount": f"K{expense_text}",
                "item_name": item_name,
                "date": formatted_datetime
            }
            self.expense_records.append(record_entry)
            self.expense_input.text = ""
            self.item_name_expense_input.text = ""
            self.show_info(f"Expense recorded: K{expense_text} for {item_name} on {formatted_datetime}")
            self.save_records()
        else:
            self.show_error("Please enter the expense amount and item name.")

    def save_records(self):
        if self.user_id:
            url = f"{FIREBASE_URL}/users/{self.user_id}.json"
            data = {
                "income_records": self.income_records,
                "expense_records": self.expense_records
            }
            response = requests.put(url, json=data)
            if response.status_code == 200:
                self.show_info("Records saved successfully!")

    def load_records(self):
        if self.user_id:
            url = f"{FIREBASE_URL}/users/{self.user_id}.json"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json() or {}
                self.income_records = data.get("income_records", [])
                self.expense_records = data.get("expense_records", [])
            else:
                self.show_error("Failed to load records from Firebase.")
    
    def save_records(self):
        with open('finance_records.json', 'w') as file:
            json.dump({
                "income_records": self.income_records,
                "expense_records": self.expense_records
            }, file)

    def load_records(self):
        try:
            with open('finance_records.json', 'r') as file:
                data = json.load(file)
                self.income_records = data.get("income_records", [])
                self.expense_records = data.get("expense_records", [])
        except FileNotFoundError:
            self.income_records = []
            self.expense_records = []

    def create_records_display(self, layout):
        # Display records
        self.record_display = BoxLayout(orientation='vertical', size_hint_y=None)
        self.record_display.bind(minimum_height=self.record_display.setter('height'))
        layout.add_widget(self.record_display)

        self.update_record_display()

    def update_record_display(self):
        self.record_display.clear_widgets()

        self.record_display.add_widget(Label(text='Income Records:', color=[1, 1, 1, 1]))
        for item in self.income_records:
            record_text = f"Income: {item['amount']} on {item['date']}"
            self.record_display.add_widget(Label(text=record_text, color=[1, 1, 1, 1]))

        self.record_display.add_widget(Label(text='Expense Records:', color=[1, 1, 1, 1]))
        for item in self.expense_records:
            record_text = f"Expense: {item['amount']} on {item['date']}"
            self.record_display.add_widget(Label(text=record_text, color=[1, 1, 1, 1]))


    def go_to_main_menu(self, instance):
        self.manager.current = 'main_menu'

    def logout(self, instance):
        self.manager.current = 'UserApp'

    def show_error(self, message):
        popup = Popup(title='Error', content=Label(text=message, color=[0, 0, 0, 1]), size_hint=(None, None), size=(400, 200))
        popup.open()

    def show_info(self, message):
        popup = Popup(title='Info', content=Label(text=message, color=[0, 0, 0, 1]), size_hint=(None, None), size=(400, 200))
        popup.open()


class MainMenuScreen(Screen):
    def __init__(self, **kwargs):
        super(MainMenuScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Background Image
        background = KivyImage(source='background.jpg', allow_stretch=True, keep_ratio=False)
        layout.add_widget(background)

        # Logo Image
        logo = KivyImage(source='logo.png', size_hint=(0.4, 0.4), pos_hint={'center_x': 0.5, 'y': 0.8})
        layout.add_widget(logo)

        title_label = Label(text='Main Menu', font_size=20)
        layout.add_widget(title_label)

        profile_button = Button(text='Profile', size_hint_y=None, height=50)
        profile_button.bind(on_release=self.edit_profile)
        layout.add_widget(profile_button)

        finance_tracker_button = Button(text='Finance Tracker', size_hint_y=None, height=50)
        finance_tracker_button.bind(on_release=self.go_to_finance_tracker)
        layout.add_widget(finance_tracker_button)

        view_record_button = Button(text='View Records', size_hint_y=None, height=50)
        view_record_button.bind(on_release=self.view_records)
        layout.add_widget(view_record_button)

        print_record_button = Button(text='Print Records', size_hint_y=None, height=50)
        print_record_button.bind(on_release=self.show_records_popup)
        layout.add_widget(print_record_button)

        self.add_widget(layout)

    def edit_profile(self, instance):
        self.manager.current = 'profile_screen'

    def go_to_finance_tracker(self, instance):
        self.manager.current = 'dashboard'
    
    def view_records(self, instance):
        self.manager.current = 'records_screen'

    def show_records_popup(self, instance):
        records_info = self.get_records_info()

        popup = Popup(title="Records", content=Label(text=records_info), size_hint=(0.8, 0.4))
        popup.open()

    def get_records_info(self):
        dashboard_screen = self.manager.get_screen('dashboard')
        user_id = dashboard_screen.user_id
        records_info = ""

        if user_id:
            # Fetch income records
            url_income = f"{FIREBASE_URL}/users/{user_id}/income_records.json"
            response_income = requests.get(url_income)
            if response_income.status_code == 200:
                income_data = response_income.json() or {}
                records_info += "Income Records:\n"
                for record in income_data:
                    records_info += f"{record['date']}: {record['item_name']} - {record['amount']}\n"

            # Fetch expense records
            url_expense = f"{FIREBASE_URL}/users/{user_id}/expense_records.json"
            response_expense = requests.get(url_expense)
            if response_expense.status_code == 200:
                expense_data = response_expense.json() or {}
                records_info += "\nExpense Records:\n"
                for record in expense_data:
                    records_info += f"{record['date']}: {record['item_name']} - {record['amount']}\n"
        
        else:
            records_info = "No records available."
        
        return records_info
    
class ProfileScreen(Screen):
    def __init__(self, **kwargs):
        super(ProfileScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.first_name_input = TextInput(hint_text='First Name', multiline=False)
        layout.add_widget(self.first_name_input)

        self.surname_input = TextInput(hint_text='Surname', multiline=False)
        layout.add_widget(self.surname_input)

        self.business_name_input = TextInput(hint_text='Business Name', multiline=False)
        layout.add_widget(self.business_name_input)

        self.registration_number_input = TextInput(hint_text='Business Registration Number', multiline=False)
        layout.add_widget(self.registration_number_input)

        self.save_button = Button(text='Save Profile', size_hint_y=None, height=50)
        self.save_button.bind(on_release=self.save_profile)
        layout.add_widget(self.save_button)

        self.add_widget(layout)

    def save_profile(self, instance):
        first_name = self.first_name_input.text
        surname = self.surname_input.text
        business_name = self.business_name_input.text
        registration_number = self.registration_number_input.text

        if first_name and surname and business_name and registration_number:
            user_id = self.manager.get_screen('Record').user_id  # Assume the user_id is still stored
            user_details = {
                "first_name": first_name,
                "surname": surname,
                "business_name": business_name,
                "registration_number": registration_number,
            }
            requests.patch(f"{FIREBASE_URL}/users/{user_id}.json", json=user_details)
            self.show_popup("Success", "Profile saved successfully!")
        else:
            self.show_popup("Error", "Please fill in all fields.")

    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message), size_hint=(0.8, 0.4))
        popup.open()

class RecordsScreen(Screen):
    def __init__(self, **kwargs):
        super(RecordsScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Header
        header = Label(text='Records', font_size=24)
        layout.add_widget(header)

        # Display income and expense records
        self.records_display = BoxLayout(orientation='vertical', size_hint_y=None)
        self.records_display.bind(minimum_height=self.records_display.setter('height'))

        layout.add_widget(self.records_display)

        # Back button to main menu
        btn_back = Button(text='Back to Main Menu', size_hint_y=None, height=50)
        btn_back.bind(on_release=self.go_to_main_menu)
        layout.add_widget(btn_back)

        self.add_widget(layout)

    def on_enter(self):
        self.populate_records()  # Now it's safe to call populate_records()

    def populate_records(self):
        # Verify that self.manager is set
        print("Current screen:", self.name)
        print("Manager is:", self.manager)  # Debugging line
        
        if self.manager:
            dashboard_screen = self.manager.get_screen('dashboard')
            self.user_id = dashboard_screen.user_id  # Get the user ID from the dashboard

            if self.user_id:
                # Fetch income records
                url_income = f"{FIREBASE_URL}/users/{self.user_id}/income_records.json"
                response_income = requests.get(url_income)
                if response_income.status_code == 200:
                    income_data = response_income.json() or {}
                    self.records_display.add_widget(Label(text='Income Records:', size_hint_y=None, height=30))
                    for record in income_data:
                        record_text = f"{record['date']}: {record['item_name']} - {record['amount']}"
                        self.records_display.add_widget(Label(text=record_text, size_hint_y=None, height=30))

                # Fetch expense records
                url_expense = f"{FIREBASE_URL}/users/{self.user_id}/expense_records.json"
                response_expense = requests.get(url_expense)
                if response_expense.status_code == 200:
                    expense_data = response_expense.json() or {}
                    self.records_display.add_widget(Label(text='Expense Records:', size_hint_y=None, height=30))
                    for record in expense_data:
                        record_text = f"{record['date']}: {record['item_name']} - {record['amount']}"
                        self.records_display.add_widget(Label(text=record_text, size_hint_y=None, height=30))

    def go_to_main_menu(self, instance):
        self.manager.current = 'main_menu'    

class MyScreenManager(ScreenManager):
    pass


class FinanceTrackerApp(App):
    def build(self):
        sm = MyScreenManager()
        login_screen = UserApp(name='UserApp')
        dashboard_screen = DashboardScreen(name='dashboard')
        main_menu_screen = MainMenuScreen(name='main_menu')
        profile_screen = ProfileScreen(name='profile_screen')
        records_screen = RecordsScreen(name='records_screen')  # Add records screen

        sm.add_widget(login_screen)
        sm.add_widget(dashboard_screen)
        sm.add_widget(main_menu_screen)
        sm.add_widget(profile_screen)
        sm.add_widget(records_screen)  # Include the RecordsScreen

        sm.current = 'UserApp'  # Start with the UserApp screen
        return sm


if __name__ == '__main__':
    FinanceTrackerApp().run()