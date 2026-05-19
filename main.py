import time
import serial
import kivy
import kivy.properties
import requests
from kivy.app import App
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.uix.image import Image

Window.size = (900,600)

try:
    pico = serial.Serial("COM4", 115200)
    time.sleep(2)
except:
    pico = None
    print(("Pico nicht verbunden"))

Builder.load_string("""
<Login>
    FloatLayout:
        canvas.before:
            Color:
                rgba: 0.12, 0.12, 0.12, 1
            Rectangle:
                pos: self.pos
                size: self.size
            Color:
                rgba: 0.1, 0.8, 0.3, 1
            Ellipse:
                pos: self.width*0.35, self.height*0.28
                size: self.width*0.3, self.width*0.3
        Label:
            text: "HS Smart-Home"
            font_size: 42
            bold: True
            color: 1, 1, 1, 1
            size_hint: (1, 0.1)
            pos_hint: {"top": 0.95}
        Image:
            source: "rfid.png"
            size_hint: (0.22, 0.22)
            pos_hint: {"center_x": 0.5, "center_y": 0.62}
            allow_stretch: True
        Label:
            text: "RFID Scan"
            font_size: 32
            bold: True
            color: 1, 1, 1, 1
            size_hint: (1, 0.05)
            pos_hint: {"center_y": 0.42}
        Label:
            text: "Chip auflegen"
            font_size: 22
            color: 0.9, 0.9, 0.9, 1
            size_hint: (1, 0.05)
            pos_hint: {"center_y": 0.37}
        Label:
            id: status_label
            text: "Status: Bereit"
            font_size: 18
            color: 0.7, 0.7, 0.7, 1
            size_hint: (1, 0.05)
            pos_hint: {"y": 0.05}
        Button:
            background_color: (0, 0, 0, 0)
            size_hint: (0.3, 0.3)
            pos_hint: {"center_x": 0.5, "center_y": 0.5}
            on_release:
                root.rfid_login()

<LadeBildschirm>:
    FloatLayout:
        canvas.before:
            Color:
                rgba: 0.12, 0.12, 0.12, 1
            Rectangle:
                pos: self.pos
                size: self.size
                    
        Image:
            source: "loading.gif"
            anim_delay: 0.05
            size_hint: (0.3, 0.3)
            pos_hint: {"center_x": 0.5, "center_y": 0.55}
                    
        Label:
            text: "Smart-Home wird geladen..."
            font_size: 24
            color: 1, 1, 1, 1
            pos_hint: {"center_y": 0.3}

<Steuerung>:
    canvas.before:
        Color:
            rgba: 0.95, 0.95, 0.95, 1
        Rectangle:
            pos: self.pos
            size: self.size
                    
    FloatLayout:  
        canvas.before:
            Color:
                rgba: 1, 1, 1, 1
            RoundedRectangle:
                pos: self.width * 0.73, self.height * 0.02
                size: self.width * 0.23, self.height * 0.18
                radius: [20]
            RoundedRectangle:
                pos: self.width * 0.33, self.height * 0.02
                size: self.width * 0.32, self.height * 0.18
                radius: [20]
                    
        Label:
            text: "Smart-Home Steuerung"
            font_size: 40
            bold: True
            color: 0,0,0,1
            size_hint: (1, 0.15)
            pos_hint: {"top": 1}
                    
        Button:
            text: "Abmelden"
            font_size: 20
            background_normal: ""
            background_color: (0.8, 0.1, 0.1, 1)
            size_hint: (0.2, 0.1)
            pos_hint: {"x": 0.02, "y": 0.02}
            on_release:
                app.root.get_screen("login").ids.status_label.text = "Status: Bereit"
                root.manager.current = "login"
                root.manager.transition.direction = "down"
                    
        Button:
            text: "Menü"
            size_hint:(0.25, 0.08)
            pos_hint: {"x": 0.02, "top": 0.82}
            font_size: 20
            background_normal: ""
            background_color: (0.2,0.2,0.2,1)
            on_release:
                root.dropdown.open(self) 

        Label:
            text: "Wetter"
            font_size: 22
            bold: True
            color: 0.1,0.1,0.1,1
            size_hint: (0.2, 0.05)
            pos_hint: {"right": 0.93, "y": 0.13} 

        Label:
            id: temperatur_label
            text: "--°C"
            font_size: 42
            bold: True
            color: 0,0,0,1
            size_hint: (0.15, 0.08)
            pos_hint: {"right": 0.84, "y": 0.055}

        Label:
            id: wetter_text_label
            text: "---"
            font_size: 18
            color: 0.3,0.3,0.3,1
            size_hint: (0.2, 0.05)
            pos_hint: {"right": 0.96, "y": 0.07}

        Label:
            text: "Kleidungsempfehlung"
            font_size: 24
            bold: True
            color: 0.1,0.1,0.1,1
            size_hint: (0.3, 0.05)
            pos_hint: {"center_x": 0.5, "y": 0.13}

        Label:
            id: kleidung_label
            text: "---"
            font_size: 19
            color: 0.35,0.35,0.35,1
            halign: "center"
            valign: "middle"
            text_size: self.size
            size_hint: (0.28, 0.08)
            pos_hint: {"center_x": 0.5, "y": 0.055}
                       
<LichtScreen>:
    FloatLayout:
        canvas.before:
            Color:
                rgba: 0.95, 0.95, 0.95, 1
            Rectangle:
                pos: self.pos
                size: self.size
            Color:
                rgba: 1, 1, 1, 1
            RoundedRectangle:
                pos: self.width * 0.3, self.height * 0.35
                size: self.width * 0.4, self.height * 0.3
                radius: [20]

        Label:
            text: "Lichtsteuerung"
            font_size: 40
            bold: True
            color: 0,0,0,1
            size_hint: (1, 0.1)
            pos_hint: {"top": 0.95}

        Label:
            text: "Wohnzimmer"
            font_size: 30
            bold: True
            color: 0.1,0.1,0.1,1
            pos_hint: {"center_y": 0.62}

        Switch:
            id: licht_switch
            size_hint: (0.15, 0.1)
            pos_hint: {"center_x": 0.5, "center_y": 0.5}
            on_active:
                root.licht_schalten(self.active)

        Label:
            id: licht_status
            text: "Licht ausgeschaltet"
            font_size: 22
            color: 0.35,0.35,0.35,1
            pos_hint: {"center_y": 0.38}

        Button:
            text: "Zurück"
            font_size: 20
            background_normal: ""
            background_color: (0.8, 0.1, 0.1, 1)
            size_hint: (0.2, 0.1)
            pos_hint: {"x": 0.02, "y": 0.02}
            on_release:
                root.manager.current = "Smart-Home"
                root.manager.transition.direction = "right"
""")

class Login(Screen):                              #Login Bildschirm

    def rfid_login(self):
        self.ids.status_label.text = "Status: Anmeldung erfolgreich"
        self.manager.current = "loading"
        self.manager.transition.direction = "left"

class LadeBildschirm(Screen):
    
    def on_enter(self):
        Clock.schedule_once(self.wechseln, 2)
    
    def wechseln(self, dt):
        screen = self.manager.get_screen("Smart-Home")
        screen.popup_anzeigen = True
        self.manager.current = "Smart-Home"
        self.manager.transition.direction = "left"

class Steuerung(Screen):                                        #Steuerungsbildschirm

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.dropdown = DropDown()

        punkte = [
            "Licht",
            "Rollläden",
            "Elektronische Geräte Übersicht",
            "Wetterdaten",
            "Sonstiges"
        ]

        for punkt in punkte:
            btn = Button(
                text=punkt,
                size_hint_y=None,
                height=60,
                font_size=20
            )

            btn.bind(on_release=lambda btn: self.menu_aktion(btn.text))
            self.dropdown.add_widget(btn)

    def lade_wetter(self):
        lat = 48.8366887
        lon = 10.0971163

        API_KEY = "9e4c6e4de178d5a36c57e963b0befaab"

        url = (
            f"https://api.openweathermap.org/data/2.5/weather?"
            f"lat={lat}&lon={lon}"
            f"&appid={API_KEY}"
            f"&units=metric"
            f"&lang=de"
        )
        response = requests.get(url)

        if response.status_code == 200:

            data = response.json()

            wetter = data["weather"][0]["description"]
            temperatur = round(data["main"]["temp"])

            if temperatur <= 0:
                empfehlung = "Winterjacke, Mütze und Handschuhe"
            elif temperatur <= 10:
                empfehlung = "Warme Jacke empfohlen"
            elif temperatur <= 18:
                empfehlung = "Pullover oder leichte Jacke"
            elif temperatur <= 25:
                empfehlung = "T-Shirt oder dünner Pullover"
            else:
                empfehlung = "Kurze Kleidung empfohlen"
            self.ids.temperatur_label.text = f"{temperatur}°C"
            self.ids.wetter_text_label.text = wetter.capitalize()
            self.ids.kleidung_label.text = empfehlung

        else:
            self.ids.wetter_text_label.text = "Wetterdaten Fehler"

    def on_enter(self):
        if self.popup_anzeigen:
            popup = Popup(
                title="Info",
                content=Label(text="Willkommen"),
                size_hint=(None, None),
                size=(300, 200)
            )
        
            popup.open()
            Clock.schedule_once(lambda dt: popup.dismiss(), 2)
            self.popup_anzeigen = False
            
        self.lade_wetter()
    
    def menu_aktion(self, text):
        self.dropdown.dismiss()
        if text == "Licht":
            self.manager.current = "licht"
            self.manager.transition.direction = "left"

popup_anzeigen = False

class LichtScreen(Screen):

    def licht_schalten(self, status):
        if status:
            self.ids.licht_status.text = "Licht eigeschaltet"
            if pico:
                pico.write(b"ON\n")
                print("ON gesendet")
        else:
            self.ids.licht_status.text = "Licht ausgeschaltet"
            if pico:
                pico.write(b"OFF\n")
                print("OFF gesendet")

ms = ScreenManager()
ms.add_widget(Login(name="login"))
ms.add_widget(LadeBildschirm(name="loading"))
ms.add_widget(Steuerung(name="Smart-Home"))
ms.add_widget(LichtScreen(name="licht"))
    
class StartApp(App):
    title = "HS Smart-Home"
    def build(self):
        return ms
    
if __name__ == "__main__":
    StartApp().run()