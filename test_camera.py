from kivymd.app import MDApp
from kivy.clock import Clock 
from kivy.uix.screenmanager import Screen,ScreenManager,FadeTransition,SwapTransition, FallOutTransition,RiseInTransition
from kivy.lang import Builder  #load file kv
from kivy.config import Config # set up firebase
import pyrebase
import threading # phân luồng dữ liệu
import time 
from firebase import firebase
from kivymd.toast import toast
from kivy.utils import platform
from plyer import notification
import pyowm
from datetime import datetime
from getpass import getpass
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
import cv2
owm = pyowm.OWM("609cbc06dacb44b7727b818875ee6923")#open weather map
pm25,temp, hum, sign_app, status_light, sign_fan_app, status_fan =   "", "", "", "","","",""
sign_app, sign_fan_app, value_btn_light, sign_btn_light = "", "", "", None
check = False
location = ""
flag_location = True
flag_user = ""
email = ""
password = ""
email_save, password_save = "", ""
flag_log_out = ""
flag_face = False

face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

app = firebase.FirebaseApplication("https://dht11-29479-default-rtdb.firebaseio.com/")

config = {
  "apiKey": "AIzaSyBtq5sxCa0Bx0EqG7UTYcnmxeW70JMW79c",
  "authDomain": "dht11-29479.firebaseapp.com",
  "databaseURL": "https://dht11-29479-default-rtdb.firebaseio.com",
  "projectId": "dht11-29479",
  "storageBucket": "dht11-29479.appspot.com",
  "messagingSenderId": "605861105328",
  "appId": "1:605861105328:web:41afb27bb16029de63f575",
  "measurementId": "G-BJ6FGB0QRQ"
}
# khoi tao firebase
firebase = pyrebase.initialize_app(config)
#lap auth cua firebase de dang nhap
auth = firebase.auth()
# lay du lieu
database = firebase.database()

class KivyCamera(Screen):
    count = 0
    def __init__(self, **kwargs):
        super(KivyCamera, self).__init__(**kwargs)
        self.event = Clock.schedule_interval(self.check_flag_face, 0.01)

    def check_flag_face(self, *args):
        global flag_face
        if flag_face == True:
            flag_face = False
            print("a")
            self.capture = cv2.VideoCapture(0)
            self.event = Clock.schedule_interval(self.update, 0.03)

    def event_button(self, *args):
        self.capture = cv2.VideoCapture(0)
        self.event = Clock.schedule_interval(self.update, 0.03)

    def update(self, dt):
        global face_cascade
        ret, frame = self.capture.read()
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray,1.1,4)
            for (x,y,w,h) in faces:
                cv2.rectangle(frame, (x,y), (x+w, y+h), (255,0,0), 2)
                self.count += 1
            if self.count == 20:
                print("true")
                self.event.cancel()
                self.capture.release()
                self.manager.current = "door"
            # convert it to texture
            buf1 = cv2.flip(frame, 0)
            buf = buf1.tostring()
            image_texture = Texture.create(
                size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            # display image from the texture
            self.ids.img.texture = image_texture

class Login(Screen):
    #init? super?
    def __init__(self, **kwargs):
        super(Login, self).__init__(**kwargs)
        Clock.schedule_interval(self.check_user, 0.01)  

    def check_user(self, *args):
        global flag_user, email, password, email_save, password_save, flag_log_out
        if check == True:
            if flag_log_out == "0":
                print("vuong")
                self.ids.id_user_name.text = ""
                self.ids.id_user_password.text = ""
                self.manager.current = "login"
                flag_log_out = ""
            else:
                if email_save and password_save and flag_user == "":
                    self.manager.current = "door"
                    flag_user = "1"
                else:
                    if flag_user == "1" and email and password:
                        print("a")
                        self.manager.current = "door"
                        #flag_user = ""
                        email = ""
                        password = ""
                    elif flag_user == "0" and email != "" and password != "":
                        toast("CHECK USER OR PASSWORD AGAIN")
                        flag_user = ""
                        email = ""
                        password = ""

    def event_sign_in(self, *args):
        global email, password
        if password_save == "" and email_save == "":
            email = self.ids.id_user_name.text
            password = self.ids.id_user_password.text
    
    def event_sign_in_with_face(self, *args):
        global flag_face
        self.manager.current = "cam"
        flag_face = True

class Bed_room(Screen):
    pass

class Door(Screen):
    flag = True
    old_location = ""
    def __init__(self, **kwargs):
        super(Door, self).__init__(**kwargs)
        # schedule_interval: lăp liên tục theo chu kì 0.01s
        Clock.schedule_interval(self.realtime_weather, 0.01)  

    def realtime_weather(self, *args):
        global owm, location, flag_location
        if location and self.flag == True:
            self.obs = owm.weather_at_place(location)
            self.weather = self.obs.get_weather()
            self.ids.id_location.text = location
            self.ids.id_sts_weather.text = self.weather.get_detailed_status()
            self.ids.dai.text = str(int(self.weather.get_temperature('celsius')["temp"])) + "°"
            self.ids.realtime_humi.text = str(int(self.weather.get_humidity())) + "%"
            self.flag = False
            self.old_location = location
        if (location == "" or self.old_location != location) and self.flag == False:
            print(location)
            self.flag = True
class Kitchen_room(Screen):
    pass

class Hello(Screen):
    temp_flag = ""
    def __init__(self, **kwargs):
        super(Hello, self).__init__(**kwargs)
        Clock.schedule_interval(self.statusLight, 0.01)
        #Clock.schedule_interval(self.statusfan, 1)
        Clock.schedule_interval(self.change_temp_hum, 2)
        Clock.schedule_interval(self.change_image, 2)

    def event_button_log_out(self, *args):
        global flag_log_out
        flag_log_out = "1"

    def event_button_light(self, *args):
        global value_btn_light, database, sign_btn_light, sign_app, status_light
        if value_btn_light == 1:
            sign_btn_light = 0
            sign_app = "off_light"
        if value_btn_light == 0:
            sign_btn_light = 1
            sign_app = "on_light"

    def event_button_fan(self, *args):
        global sign_fan_app, database, flag_fan
        print("fan")

    def change_image(self, *args):
        global pm25
        if pm25:
            self.pm25 = pm25.split()
            self.pm25 = float(self.pm25[0])
            if 0 < self.pm25 and self.pm25 < 12:
                self.ids.emotion.source = 'happy.png'
            elif 12.1 < self.pm25 and self.pm25 < 35.4:
                self.ids.emotion.source = 'smile.png'
            elif 35.5 < self.pm25 and self.pm25 < 55.4:
                self.ids.emotion.source = 'meh.png'
            elif 55.5 < self.pm25 and self.pm25 < 150.4:
                self.ids.emotion.source = 'sad.png'
            elif 150.5 < self.pm25 and self.pm25 < 250.4:
                self.ids.emotion.source = 'bad.png'
            elif self.pm25 > 250.5:
                self.ids.emotion.source = 'bored.png'

    def statusLight(self, *args):
        global sign_app, value_btn_light, status_light, sign_btn_light
        if sign_app == "on_light" or status_light == "on":
            self.ids.btn_light.text_color = (242/255, 217/255, 116/255,1)
            self.ids.cover_light.text_color = (37/255, 37/255, 37/255,1)
            self.ids.card_coverlight.opacity = 0.4
            value_btn_light = 1
            sign_app = ""
        if sign_app == "off_light" or status_light == "off":
            value_btn_light = 0
            sign_app = ""
            self.ids.btn_light.text_color = (97/255, 97/255, 97/255,1)
            self.ids.cover_light.text_color = (97/255, 97/255, 97/255,1)
            self.ids.card_coverlight.opacity = 0.2
        if temp > "30°C" and temp != self.temp_flag:
            notification.notify(
                title="Temperature",
                message="warnning",
                app_name="Waentjies",
                app_icon="happy.ico",
                timeout=10)
            self.temp_flag = temp
            self.ids.weather.source = 'rain.png'

    def statusfan(self, *args):
        global status_fan
        print(status_fan)
        if status_fan == "on":
            self.ids.switch_fan.active = True
        else:
            self.ids.switch_fan.active = False
    
    def change_temp_hum(self, *args):
        global temp, hum
        self.ids.label_temp.text = temp
        self.ids.label_hum.text = hum
        self.ids.label_pm.text = pm25

Builder.load_file("helper.kv")

class DemoApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    def build(self):
        self.sm = ScreenManager(transition= FallOutTransition())
        self.sm.add_widget(Login(name='login'))
        self.sm.add_widget(Door(name='door'))
        self.sm.add_widget(KivyCamera(name='cam'))
        self.sm.add_widget(Hello(name='hello'))   
        self.sm.add_widget(Bed_room(name = 'bedroom'))
        self.sm.add_widget(Kitchen_room(name = 'kitchenroom'))
        self.theme_cls.primary_palette = 'Gray'
        self.theme_cls.primary_hue = '800'
        #screen = Builder.load_file("helper.kv")
        self.theme_cls.theme_style = 'Light'
        return self.sm
    
    def on_start(self):
        from kivy.base import EventLoop
        EventLoop.window.bind(on_keyboard=self.hook_keyboard)

    def hook_keyboard(self, window, key, *largs):
        global sm
        if key == 27:
            self.sm.current = self.sm.previous()
            #notification.notify(title="Kivy Notification",message="Plyer Up and Running!",app_name="Waentjies",app_icon="happy.ico",timeout=10)
            return True

def login():
    global flag_user, email, password, auth,flag_log_out
    while True:
        if email and password:
            print("b")
            try:
                auth.sign_in_with_email_and_password(email, password)
                app.put("/DHT11", "password_save", password)
                app.put("/DHT11", "email_save", email)
                flag_user = "1"
            except:
                flag_user = "0"

        if flag_log_out == "1":
            app.put("/DHT11", "password_save", "")
            app.put("/DHT11", "email_save", "")
            flag_log_out = "0"
        time.sleep(0.05)

def get_data():
    global flag_location,location,pm25,temp, hum, database, status_light, status_fan, sign_fan_app, sign_app, flag_light, app, check, email_save, password_save
    flag = True
    while True:
        try:
            data = database.child("DHT11").get()
            email_save = data.val()["email_save"]
            password_save = data.val()["password_save"]
            hum = data.val()["hum"]
            temp = data.val()["temp"]
            pm25 = data.val()["PM2_5"]
            location = data.val()["location"]
            status_light = data.val()["status_light"]
            status_fan = data.val()["status_fan"]
            sign_app = data.val()["sign_app"]
            sign_fan_app = data.val()["sign_fan_app"]
            flag = True
            check = True
        except:
            if flag == True:
                toast("CONNECTION FAILED!")
                flag = False
                check = False
        time.sleep(0.05)

def send_data():
    global value_btn_light, database, sign_btn_light, app, flag_user, email, password
    while True:
        try:
            if sign_btn_light == 0:
                print("off")
                app.put("/DHT11", "sign_app", "off_light")
                app.put("/DHT11", "sign_app_temp", "off_light")
                sign_btn_light = None
            if sign_btn_light == 1:
                print("on")
                app.put("/DHT11", "sign_app", "on_light")
                app.put("/DHT11", "sign_app_temp", "on_light")
                sign_btn_light = None
        except:
            if sign_btn_light != None:
                toast("CONNECTION FAILED!")
                sign_btn_light = None
        time.sleep(0.05)

threading.Thread(target=get_data).start()
threading.Thread(target=send_data).start()
threading.Thread(target=login).start()
DemoApp().run()
