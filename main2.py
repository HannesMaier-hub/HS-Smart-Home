import time
import kivy
import kivy.properties
import requests
import serial
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
from datetime import datetime
from collections import deque       #Algorithmen und Datenstrukturen

#Größe des Fensters für die GUI
Window.size = (900, 600)

#Visuelle Design der GUI
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
            #ändert Text
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
            #ruft beim klicken die Methode rfid_login der Klasse login auf
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
                    
    canvas:
        Color:
            rgba: 0.85, 0.85, 0.85, 1
        Line:
            points: self.width * 0.66, self.height * 0.11, self.width * 0.92, self.height * 0.11
            width: 1.2
                    
    FloatLayout:  
        canvas.before:
                #Hintergrundbox vom Wetter
            Color:
                rgba: 1, 1, 1, 1
            RoundedRectangle:
                pos: self.width * 0.60, self.height * 0.03
                size: self.width * 0.34, self.height * 0.26
                radius: [25]
            Color:
                rgba: 0.88, 0.88, 0.88, 1
            Line:
                points:
                    self.width * 0.62, self.height * 0.10, self.width * 0.92, self.height * 0.10
                width: 1

                #Hintergrundbox der Übersicht   
            Color:
                rgba: 1, 1, 1, 1        
            RoundedRectangle:
                pos: self.width * 0.06, self.height * 0.03
                size: self.width * 0.5, self.height * 0.80
                radius: [25]
                    
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
            size_hint: (0.12, 0.05)
            pos_hint: {"x": 0.02, "y": 0.9}
            #setzt den Status-Text im Login-Screen zurück und wechselt dorthin
            on_release:
                app.root.get_screen("login").ids.status_label.text = "Status: Bereit"
                root.manager.current = "login"
                root.manager.transition.direction = "down"
                    
        Button:
            text: "Menü"
            size_hint:(0.25, 0.08)
            pos_hint: {"x": 0.67, "top": 0.82}
            font_size: 20
            background_normal: ""
            background_color: (0.2,0.2,0.2,1)
            #Öffnet das Dropdown-Menü
            on_release:                     
                root.dropdown.open(self) 

            #Wetter Anzeige
            #IDs werden in der Methode lade_wetter mit den echten APIs befüllt
        Label:
            text: "Wetter in 3h"
            font_size: 22
            bold: True
            color: 0.15,0.15,0.15,1
            size_hint: (0.2, 0.04)
            pos_hint: {"x": 0.67, "y": 0.22}

        Label:
            id: ort_label
            text: "Aalen"
            font_size: 17
            color: 0.45, 0.45, 0.45, 1
            size_hint: (0.15, 0.03)
            pos_hint: {"x": 0.81, "y": 0.22}
                    
        Label:
            id: zeit_label
            text: "--:-- Uhr"
            font_size: 16
            color: 0.45, 0.45, 0.45, 1
            size_hint: (0.15, 0.03)
            pos_hint: {"x": 0.81, "y": 0.18}

        Label:
            id: temperatur_label
            text: "--°C"
            font_size: 48
            bold: True
            color: 0.05,0.05,0.05,1
            size_hint: (0.2, 0.08)
            pos_hint: {"x": 0.57, "y": 0.11}

        Label:
            id: wetter_text_label
            text: "---"
            font_size: 20
            bold: True
            color: 0.18,0.55,0.25,1
            size_hint: (0.25, 0.04)
            pos_hint: {"center_x": 0.80, "y": 0.13}

        Label:
            text: "Kleidungsempfehlung"
            font_size: 18
            color: 0.5,0.5,0.5,1
            size_hint: (0.2, 0.03)
            pos_hint: {"x": 0.67, "y": 0.065}

        Label:
            id: kleidung_label
            text: "---"
            font_size: 17
            bold: True
            color: 0.15,0.15,0.15,1
            halign: "left"
            text_size: self.size
            size_hint: (0.28, 0.03)
            pos_hint: {"x": 0.69, "y": 0.04}
                    
            #Übersicht
        BoxLayout:
            orientation: "vertical"
            size_hint: (0.5, 0.80)
            pos_hint: {"x": 0.06, "y": 0.03}
            padding: [35, 40, 35, 40]
            spacing: 15

            Label:
                text: "Übersicht"
                font_size: 32
                bold: True
                color: 0.15, 0.15, 0.15, 1
                size_hint_y: None
                height: 45
                halign: "left"
                text_size: self.size
                    
            Label:
                text: "Licht"
                font_size: 26
                bold: True
                color: 0.15, 0.15, 0.15, 1
                size_hint_y: None
                height: 35
                halign: "left"
                text_size: self.size

                #Wohnzimmer-Licht
            BoxLayout:
                orientation: "horizontal"
                size_hint_y: None
                height: 40
                padding: [15, 0, 0, 0]
                    
                Label:
                    text: "Wohnzimmer"
                    font_size: 21
                    color: 0.2, 0.2, 0.2, 1
                    halign: "left"
                    text_size: self.size
                
                Label:
                    id: wohnzimmer_licht_status
                    text: "AUS"
                    font_size: 13
                    bold: True
                    color: 1, 1, 1, 1
                    size_hint: (None, None)
                    size: (65, 30)
                    pos_hint: {"center_y": 0.5}
                    halign: "center"
                    valign: "middle"
                    canvas.before:
                        Color:
                            #rgba: rot falls AUS, grün wenn EIN
                            rgba: (0.8, 0.15, 0.15, 1) if self.text == "AUS" else (0.15, 0.65, 0.2, 1)
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [10]
                    
                #Küchen-Licht
            BoxLayout:
                orientation: "horizontal"
                size_hint_y: None
                height: 40
                padding: [15, 0, 0, 0]
            
                Label:
                    text: "Küche"
                    font_size: 21
                    color: 0.2, 0.2, 0.2, 1
                    halign: "left"
                    text_size: self.size
                
                Label:
                    id: kueche_licht_status
                    text: "AUS"
                    font_size: 13
                    bold: True
                    color: 1, 1, 1, 1
                    size_hint: (None, None)
                    size: (65, 30)
                    pos_hint: {"center_y": 0.5}
                    halign: "center"
                    valign: "middle"
                    canvas.before:
                        Color:
                            #rgba: rot falls AUS, grün wenn EIN
                            rgba: (0.8, 0.15, 0.15, 1) if self.text == "AUS" else (0.15, 0.65, 0.2, 1)
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [10]

                #Büro-Licht
            BoxLayout:
                orientation: "horizontal"
                size_hint_y: None
                height: 40
                padding: [15, 0, 0, 0]
            
                Label:
                    text: "Büro"
                    font_size: 21
                    color: 0.2, 0.2, 0.2, 1
                    halign: "left"
                    text_size: self.size
                
                Label:
                    id: buero_licht_status
                    text: "AUS"
                    font_size: 13
                    bold: True
                    color: 1, 1, 1, 1
                    size_hint: (None, None)
                    size: (65, 30)
                    pos_hint: {"center_y": 0.5}
                    halign: "center"
                    valign: "middle"
                    canvas.before:
                        Color:
                            #rgba: rot falls AUS, grün wenn EIN
                            rgba: (0.8, 0.15, 0.15, 1) if self.text == "AUS" else (0.15, 0.65, 0.2, 1)
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [10]

                #Schlafzimmer-Licht
            BoxLayout:
                orientation: "horizontal"
                size_hint_y: None
                height: 40
                padding: [15, 0, 0, 0]
            
                Label:
                    text: "Schlafzimmer"
                    font_size: 21
                    color: 0.2, 0.2, 0.2, 1
                    halign: "left"
                    text_size: self.size
                
                Label:
                    id: schlafzimmer_licht_status
                    text: "AUS"
                    font_size: 13
                    bold: True
                    color: 1, 1, 1, 1
                    size_hint: (None, None)
                    size: (65, 30)
                    pos_hint: {"center_y": 0.5}
                    halign: "center"
                    valign: "middle"
                    canvas.before:
                        Color:
                            #rgba: rot falls AUS, grün wenn EIN
                            rgba: (0.8, 0.15, 0.15, 1) if self.text == "AUS" else (0.15, 0.65, 0.2, 1)
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [10]      

            #Platzhalter             
            Widget:
                size_hint_y: None
                height: 10
                    
            Label:
                text: "Rollläden"
                font_size: 26
                bold: True
                color: 0.15, 0.15, 0.15, 1
                size_hint_y: None
                height: 35
                halign: "left"
                text_size: self.size
                    
                #Wohnzimmer-Rollläden
            BoxLayout:
                orientation: "horizontal"
                size_hint_y: None
                height: 40
                padding: [15, 0, 0, 0]
                
                Label:
                    text: "Wohnzimmer"
                    font_size: 21
                    color: 0.2, 0.2, 0.2, 1
                    halign: "left"
                    text_size: self.size

                Label:
                    id: wohnzimmer_rollladen_status
                    text: "OFFEN"
                    font_size: 13
                    bold: True
                    color: 1, 1, 1, 1
                    size_hint: (None, None)
                    size: (70, 30)
                    pos_hint: {"center_y": 0.5}
                    halign: "center"
                    valign: "middle"
                    canvas.before:
                        Color:
                            rgba: (0.15, 0.65, 0.25, 1) if self.text == "OFFEN" else (0.8, 0.15, 0.15, 1)
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [10]
                    
            Widget:
                size_hint_y: None
                height: 15
                    
            Label:
                text: "Letzte Aktivitäten (Queue):"
                font_size: 20
                bold: True
                color: 0.3, 0.3, 0.3, 1
                size_hint_y: None
                height: 25
                halign: "left"
                text_size: self.size
            Label:
                id: log_anzeige
                text: "Noch keine Aktivitäten"
                font_size: 15
                color: 0.2, 0.2, 0.2, 1
                halign: "left"
                valign: "top"
                text_size: self.size
                padding: [15, 12]
                size_hint_y: None
                height: 90
                canvas.before:
                    Color:
                        rgba: 0.92, 0.92, 0.92, 1
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [10]
                        
<LichtScreen>:
    canvas.before:
        Color:
            rgba: 0.95, 0.95, 0.95, 1
        Rectangle:
            pos: self.pos
            size: self.size
    
    FloatLayout:
        Label:
            text: "Lichtsteuerung"
            font_size: 40
            bold: True
            color: 0,0,0,1
            size_hint: (1, 0.1)
            pos_hint: {"top": 0.95}

        BoxLayout:
            orientation: "horizontal"
            size_hint: (0.8, 0.4)
            pos_hint: {"center_x": 0.5, "center_y": 0.55}
            spacing: 40
                    
            #Wohnzimmer-Licht
            BoxLayout:
                orientation: "vertical"
                padding: 20
                spacing: 10
                canvas.before:
                    Color:
                        rgba: 1, 1, 1, 1
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [20]
                Label:
                    text: "Wohnzimmer"
                    font_size: 26
                    bold: True
                    color: 0.1,0.1,0.1,1

                    #Schalter fürs Licht umschalten
                Switch:
                    id: licht_switch_wz
                    size_hint_y: None
                    height: 40
                    #ruft bei klicken die Methode licht_schalten auf und übergibt True/False
                    on_active:                           
                        root.licht_schalten("wohnzimmer", self.active)

                Label:
                    id: licht_status_wz
                    text: "Licht ausgeschaltet"
                    font_size: 18
                    color: 0.35,0.35,0.35,1

            #Küchen-Licht      
            BoxLayout:
                orientation: "vertical"
                padding: 20
                spacing: 10
                canvas.before:
                    Color:
                        rgba: 1, 1, 1, 1
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [20]
                Label:
                    text: "Küche"
                    font_size: 26
                    bold: True
                    color: 0.1,0.1,0.1,1

                    #Schalter fürs Licht umschalten
                Switch:
                    id: licht_switch_k
                    size_hint_y: None
                    height: 40
                    #ruft bei klicken die Methode licht_schalten auf und übergibt True/False
                    on_active:                           
                        root.licht_schalten("kueche", self.active)

                Label:
                    id: licht_status_k
                    text: "Licht ausgeschaltet"
                    font_size: 18
                    color: 0.35,0.35,0.35,1

            #Büro-Licht
            BoxLayout:
                orientation: "vertical"
                padding: 20
                spacing: 10
                canvas.before:
                    Color:
                        rgba: 1, 1, 1, 1
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [20]
                Label:
                    text: "Büro"
                    font_size: 26
                    bold: True
                    color: 0.1,0.1,0.1,1

                    #Schalter fürs Licht umschalten
                Switch:
                    id: licht_switch_b
                    size_hint_y: None
                    height: 40
                    #ruft bei klicken die Methode licht_schalten auf und übergibt True/False
                    on_active:                           
                        root.licht_schalten("buero", self.active)

                Label:
                    id: licht_status_b
                    text: "Licht ausgeschaltet"
                    font_size: 18
                    color: 0.35,0.35,0.35,1

            #Schlafzimmer-Licht
            BoxLayout:
                orientation: "vertical"
                padding: 20
                spacing: 10
                canvas.before:
                    Color:
                        rgba: 1, 1, 1, 1
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [20]
                Label:
                    text: "Schlafzimmer"
                    font_size: 26
                    bold: True
                    color: 0.1,0.1,0.1,1

                    #Schalter fürs Licht umschalten
                Switch:
                    id: licht_switch_sz
                    size_hint_y: None
                    height: 40
                    #ruft bei klicken die Methode licht_schalten auf und übergibt True/False
                    on_active:                           
                        root.licht_schalten("schlafzimmer", self.active)

                Label:
                    id: licht_status_sz
                    text: "Licht ausgeschaltet"
                    font_size: 18
                    color: 0.35,0.35,0.35,1

        Button:
            text: "Zurück"
            font_size: 20
            background_normal: ""
            background_color: (0.8, 0.1, 0.1, 1)
            size_hint: (0.2, 0.1)
            pos_hint: {"x": 0.04, "y": 0.04}
            #geht zurück zum Hauptmenü
            on_release:                            
                root.manager.current = "Smart-Home"
                root.manager.transition.direction = "right"
""")

#Logik des ersten (Anmelde)-Bildschirm
class Login(Screen):
    def rfid_login(self):
        self.ids.status_label.text = "Status: Anmeldung erfolgreich"       #Verknüpfung Kv-String
        App.get_running_app().log_event("User eingeloggt mit RFID")         #Queue
        self.manager.current = "loading"                                    #schaltet ScreenManager auf Ladebildschirm um
        self.manager.transition.direction = "left"




"""Weiß noch nicht ob drinlassen?!"""
#Vorerst nur zum testen von GIF
#Logik des (Lade)-Bildschirms
class LadeBildschirm(Screen):
    def on_enter(self):
        Clock.schedule_once(self.wechseln, 2)           #Verzögerung 2 Sekunden, dann self.wechseln
    
    def wechseln(self, dt):
        screen = self.manager.get_screen("Smart-Home")
        #Popup Willkommen anzeigen
        screen.popup_anzeigen = True
        #wechselt zur Hauptsteuerung
        self.manager.current = "Smart-Home"
        self.manager.transition.direction = "left"



#Hauptmenü
class Steuerung(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #erstellt Kivy Dropdown im Hintergrund
        self.dropdown = DropDown()
        punkte = [
            "Licht",
            "Rollläden",
            "Sensoren",
            "Wetterdaten",
            "Sonstiges"
        ]

        #Schleife für die Buttons des Dropdown-Menüs
        for punkt in punkte:
            btn = Button(
                text=punkt,
                size_hint_y=None,
                height=60,
                font_size=20
            )
            #ruft beim klicken auf einen Punkt des Dropdowns self.menu_aktion auf
            btn.bind(on_release=lambda x: self.menu_aktion(x.text))
            self.dropdown.add_widget(btn)

    def lade_wetter(self, dt=0):
        lat = 48.8366887
        lon = 10.0971163
        API_KEY = "9e4c6e4de178d5a36c57e963b0befaab"

        url = (
            f"https://api.openweathermap.org/data/2.5/forecast?"
            f"lat={lat}&lon={lon}"
            f"&appid={API_KEY}"
            f"&units=metric"
            f"&lang=de"
        )
        
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                vorhersage = data["list"][0]
                timestamp = vorhersage["dt"]
                dt_object = datetime.fromtimestamp(timestamp)
                uhrzeit = dt_object.strftime("%H:%M")
                wetter = vorhersage["weather"][0]["description"]
                temperatur = round(vorhersage["main"]["temp"])
                ort = data["city"]["name"]

                #Kleidungsempfehlung vorerst nur mit Temperatur
                if temperatur <= 0:
                    empfehlung = "Winterjacke, Mütze und Handschuhe"
                elif temperatur <= 10:
                    empfehlung = "Warme Jacke empfohlen"
                elif temperatur <= 16:
                    empfehlung = "Pullover oder leichte Jacke"
                elif temperatur <= 21:
                    empfehlung = "T-Shirt oder dünner Pullover"
                else:
                    empfehlung = "Kurze Kleidung empfohlen"
                
                #Überschreibung des Kv-Strings mit den echten APIs
                self.ids.temperatur_label.text = f"{temperatur}°C"
                self.ids.ort_label.text = ort
                self.ids.zeit_label.text = f"{uhrzeit} Uhr"
                self.ids.wetter_text_label.text = wetter.capitalize()
                self.ids.kleidung_label.text = empfehlung
            else:
                self.ids.wetter_text_label.text = "Wetterdaten Fehler"
                
        except Exception:
            self.ids.wetter_text_label.text = "Netzwerkfehler"

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
            
        #erst kurz nach dem Laden der Seite werden Wetterdaten aktualisiert, sonst Fehler
        Clock.schedule_once(self.lade_wetter, 0.1)
    
    def menu_aktion(self, text):
        #Klicks auf dem Dropdown
        self.dropdown.dismiss()     #schließt Dropdown
        if text == "Licht":
            self.manager.current = "licht"
            self.manager.transition.direction = "left"

    popup_anzeigen = False

#Schalter für die Beleuchtung
class LichtScreen(Screen):
    def licht_schalten(self, raum, status):
        steuerung = self.manager.get_screen("Smart-Home")
        app = App.get_running_app()
        
        # Status-Text und UI-Anpassungen vornehmen
        if raum == "wohnzimmer":
            self.ids.licht_status_wz.text = "Licht eingeschaltet" if status else "Licht ausgeschaltet"
            steuerung.ids.wohnzimmer_licht_status.text = "EIN" if status else "AUS"
            app.log_event(f"Wohnzimmer Licht {'AN' if status else 'AUS'}")
        elif raum == "kueche":
            self.ids.licht_status_k.text = "Licht eingeschaltet" if status else "Licht ausgeschaltet"
            steuerung.ids.kueche_licht_status.text = "EIN" if status else "AUS"
            app.log_event(f"Küche Licht {'AN' if status else 'AUS'}")
        elif raum == "buero":
            self.ids.licht_status_b.text = "Licht eingeschaltet" if status else "Licht ausgeschaltet"
            steuerung.ids.buero_licht_status.text = "EIN" if status else "AUS"
            app.log_event(f"Büro Licht {'AN' if status else 'AUS'}")
        elif raum == "schlafzimmer":
            self.ids.licht_status_sz.text = "Licht eingeschaltet" if status else "Licht ausgeschaltet"
            steuerung.ids.schlafzimmer_licht_status.text = "EIN" if status else "AUS"
            app.log_event(f"Schlafzimmer Licht {'AN' if status else 'AUS'}")

        # Befehl via App-Klasse an den Pico senden
        status_wert = "1" if status else "0"
        app.sende_an_pico(f"{raum}:{status_wert}")
                                  

ms = ScreenManager()
#Fügt die Bildschirme dem Manager zu
ms.add_widget(Login(name="login"))
ms.add_widget(LadeBildschirm(name="loading"))
ms.add_widget(Steuerung(name="Smart-Home"))
ms.add_widget(LichtScreen(name="licht"))
    
class StartApp(App):
    title = "HS Smart-Home"
    #Datenstruktur
    aktivitaeten_queue = deque(maxlen=3)        #max 3 Einträge

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ser = None
        try:
            self.ser = serial.Serial(port='COM5', baudrate=115200, timeout=1)
            time.sleep(1) # Kurze Pause für den Verbindungsaufbau
            print("Verbindung zum Pico erfolgreich hergestellt!")
        except Exception as e:
            print(f"WARNUNG: Konnte Verbindung zum Pico nicht öffnen: {e}")

    def sende_an_pico(self, befehl):
        if self.ser and self.ser.is_open:
            try:
                # Wichtig: CircuitPython braucht das '\n' um readline() zu beenden
                self.ser.write(f"{befehl}\n".encode('utf-8'))
            except Exception as e:
                print(f"Fehler beim Senden an Pico: {e}")
        else:
            print(f"Pico nicht verbunden. Befehl '{befehl}' wurde verworfen.")

    def log_event(self, text):
        #Zeitstempel
        zeit = datetime.now().strftime("%H:%M:%S")
        eintrag = f"[{zeit}] {text}"
        #In Queue einfügen
        self.aktivitaeten_queue.append(eintrag)
        #für Kivy formatieren
        anzeige_text = "\n".join(self.aktivitaeten_queue)
        #an Label in der GUI übergeben
        try:
            steuerung_screen = self.root.get_screen("Smart-Home")
            steuerung_screen.ids.log_anzeige.text = anzeige_text
        except Exception:
            pass

    def build(self):
        return ms           #Startet die App
    
if __name__ == "__main__":
    StartApp().run()