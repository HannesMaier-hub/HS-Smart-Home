import math     #test
import time
import kivy
import kivy.properties
import requests
import serial
import json
from kivy.app import App
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.factory import Factory
from datetime import datetime
from collections import deque       #Algorithmen und Datenstrukturen
from kivy.properties import NumericProperty     #test
from kivy.uix.widget import Widget              #test

#Größe des Fensters für die GUI
Window.size = (900, 600)

#Visuelle Design der GUI
Builder.load_string("""

#test                        
<SonnenVerlauf>:
    canvas:
        #Graue Linie-Sonnenverlauf
        Color:
            rgba: 0.8, 0.8, 0.8, 1
        Line:
            ellipse: (self.center_x - 70, self.y - 60, 140, 140, 270, 450)
            width: 2

        #Gelber Kreis(Sonne)       
        Color:
            rgba: 0.95, 0.75, 0.1, 1
        Ellipse:
            pos: self.sonnen_x, self.sonnen_y
            size: 20, 20

<DropdownButton@Button>:
    size_hint_y: None
    height: 50
    font_size: 18
    background_normal: ""
    background_color: (0, 0, 0, 0)
    color: (1, 1, 1, 1)
    canvas.before:
        Color:
            rgba: (0.22, 0.22, 0.22, 1) if self.state == "normal" else (0.3, 0.3, 0.3, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [10]

<Login>:
    FloatLayout:
        canvas.before:
            Color:
                rgba: 0.12, 0.12, 0.12, 1
            Rectangle:
                pos: self.pos
                size: self.size
            #Grüner Kreis-Hintergrund
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
        #Button um RFID-Scan zu simulieren
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
        #Heller Hintergrund Hauptsteuerung
        Color:
            rgba: 0.95, 0.95, 0.95, 1
        Rectangle:
            pos: self.pos
            size: self.size
                    
    canvas:
        Color:
            rgba: 0.85, 0.85, 0.85, 1
                    
    FloatLayout:  
        canvas.before:
                #Hintergrundbox vom Wetter
            Color:
                rgba: 1, 1, 1, 1
            RoundedRectangle:
                pos: self.width * 0.60, self.height * 0.03
                size: self.width * 0.34, self.height * 0.26
                radius: [25]
            #Linie Kleidungsempfehlung
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
        
        Label:
            id: live_zeit_label
            text: "Lade Datum, Uhrzeit..."
            font_size: 20
            color: 0.4, 0.4, 0.4, 1
            size_hint: (1, None)
            height: 25
            pos_hint: {"center_x": 0.5, "top": 0.89}
            halign: "center"
            valign: "middle"
                    
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
            background_color: (0, 0, 0, 0)
            color: (1, 1, 1, 1)
            canvas.before:
                Color:
                    rgba: (0.2, 0.2, 0.2, 1) if self.state == "normal" else (0.15, 0.15, 0.15, 1)
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [12]
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
            text: "---"
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
            font_size: 14
            color: 0.5,0.5,0.5,1
            size_hint: (0.3, 0.025)
            pos_hint: {"x": 0.62, "y": 0.075}
            halign: "center"
            valign: "middle"
            text_size: self.size

        Label:
            id: kleidung_label
            text: "---"
            font_size: 14
            bold: True
            color: 0.15,0.15,0.15,1
            halign: "center"
            valign: "top"
            text_size: self.size
            size_hint: (0.3, 0.05)
            pos_hint: {"x": 0.62, "y": 0.025}
                    
            #Haupt-Layout Übersicht
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
                    
            BoxLayout:
                orientation: "horizontal"
                spacing: 15
                
                #Linke Seite Lichter
                BoxLayout:
                    orientation: "vertical"
                    spacing: 5
                    
                    Label:
                        text: "Licht"
                        font_size: 24
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
                    
                        Label:
                            text: "Wohnzimmer"
                            font_size: 17
                            color: 0.2, 0.2, 0.2, 1
                            halign: "left"
                            text_size: self.size
                
                        Label:
                            id: wohnzimmer_licht_status
                            text: "AUS"
                            font_size: 12
                            bold: True
                            color: 1, 1, 1, 1
                            size_hint: (None, None)
                            size: (55, 25)
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
                                    radius: [8]
                    
                    #Küchen-Licht
                    BoxLayout:
                        orientation: "horizontal"
                        size_hint_y: None
                        height: 40
            
                        Label:
                            text: "Küche"
                            font_size: 17
                            color: 0.2, 0.2, 0.2, 1
                            halign: "left"
                            text_size: self.size
                
                        Label:
                            id: kueche_licht_status
                            text: "AUS"
                            font_size: 12
                            bold: True
                            color: 1, 1, 1, 1
                            size_hint: (None, None)
                            size: (55, 25)
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
                                    radius: [8]

                    #Büro-Licht
                    BoxLayout:
                        orientation: "horizontal"
                        size_hint_y: None
                        height: 40
            
                        Label:
                            text: "Büro"
                            font_size: 17
                            color: 0.2, 0.2, 0.2, 1
                            halign: "left"
                            text_size: self.size
                
                        Label:
                            id: buero_licht_status
                            text: "AUS"
                            font_size: 12
                            bold: True
                            color: 1, 1, 1, 1
                            size_hint: (None, None)
                            size: (55, 25)
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
                                    radius: [8]

                    #Außenbeleuchtung
                    BoxLayout:
                        orientation: "horizontal"
                        size_hint_y: None
                        height: 40
                        spacing: 5
            
                        Label:
                            text: "Außenbeleuchtung"
                            font_size: 17
                            color: 0.2, 0.2, 0.2, 1
                            halign: "left"
                            text_size: self.size
                
                        Label:
                            id: außenbeleuchtung_licht_status
                            text: "AUS"
                            font_size: 12
                            bold: True
                            color: 1, 1, 1, 1
                            size_hint: (None, None)
                            size: (55, 25)
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
                                    radius: [8]  

                        Label:
                            id: außenbeleuchtung_modus_status
                            text: "MANUELL"
                            font_size: 11
                            bold: True
                            color: 1, 1, 1, 1
                            size_hint: (None, None)
                            size: (65, 25)
                            pos_hint: {"center_y": 0.5}
                            halign: "center"
                            valign: "middle"
                            canvas.before:
                                Color:
                                    rgba: (0.8, 0.15, 0.15, 1) if self.text == "MANUELL" else (0.15, 0.65, 0.2, 1)
                                RoundedRectangle:
                                    pos: self.pos
                                    size: self.size
                                    radius: [8]

                    #Platzhalter             
                    Widget:

                #Rechte Seite Rollläden
                BoxLayout:
                    orientation: "vertical"
                    spacing: 5
                    
                    Label:
                        text: "Rollläden"
                        font_size: 24
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
                        pos_hint: {"center_y": 0.5}
                
                        Label:
                            text: "Wohnzimmer"
                            font_size: 17
                            color: 0.2, 0.2, 0.2, 1
                            halign: "left"
                            valign: "middle"
                            text_size: self.size

                        Label:
                            id: wohnzimmer_rollladen_status
                            text: "OFFEN"
                            font_size: 11
                            bold: True
                            color: 1, 1, 1, 1
                            size_hint: (None, None)
                            size: (55, 25)
                            pos_hint: {"center_y": 0.5}
                            halign: "center"
                            valign: "middle"
                            canvas.before:
                                Color:
                                    rgba: (0.15, 0.65, 0.25, 1) if self.text == "OFFEN" else (0.8, 0.15, 0.15, 1)
                                RoundedRectangle:
                                    pos: self.pos
                                    size: self.size
                                    radius: [8]
                    
                        Label:
                            id: wohnzimmer_rollladen_modus
                            text: "MANUELL"
                            font_size: 11
                            bold: True
                            color: 1, 1, 1, 1
                            size_hint: (None, None)
                            size: (65, 25)
                            pos_hint: {"center_y": 0.5}
                            halign: "center"
                            valign: "middle"
                            canvas.before:
                                Color:
                                    rgba: (0.8, 0.15, 0.15, 1) if self.text == "MANUELL" else (0.15, 0.65, 0.2, 1)
                                RoundedRectangle:
                                    pos: self.pos
                                    size: self.size
                                    radius: [8]
                    
                    #Küche-Rollläden
                    BoxLayout:
                        orientation: "horizontal"
                        size_hint_y: None
                        height: 40
                        pos_hint: {"center_y": 0.5}
                
                        Label:
                            text: "Küche"
                            font_size: 17
                            color: 0.2, 0.2, 0.2, 1
                            halign: "left"
                            valign: "middle"
                            text_size: self.size

                        Label:
                            id: kueche_rollladen_status
                            text: "OFFEN"
                            font_size: 11
                            bold: True
                            color: 1, 1, 1, 1
                            size_hint: (None, None)
                            size: (55, 25)
                            pos_hint: {"center_y": 0.5}
                            halign: "center"
                            valign: "middle"
                            canvas.before:
                                Color:
                                    rgba: (0.15, 0.65, 0.25, 1) if self.text == "OFFEN" else (0.8, 0.15, 0.15, 1)
                                RoundedRectangle:
                                    pos: self.pos
                                    size: self.size
                                    radius: [8]
                    
                        Label:
                            id: kueche_rollladen_modus
                            text: "MANUELL"
                            font_size: 11
                            bold: True
                            color: 1, 1, 1, 1
                            size_hint: (None, None)
                            size: (65, 25)
                            pos_hint: {"center_y": 0.5}
                            halign: "center"
                            valign: "middle"
                            canvas.before:
                                Color:
                                    rgba: (0.8, 0.15, 0.15, 1) if self.text == "MANUELL" else (0.15, 0.65, 0.2, 1)
                                RoundedRectangle:
                                    pos: self.pos
                                    size: self.size
                                    radius: [8]
                    
                    #Büro-Rollläden
                    BoxLayout:
                        orientation: "horizontal"
                        size_hint_y: None
                        height: 40
                        pos_hint: {"center_y": 0.5}
                
                        Label:
                            text: "Büro"
                            font_size: 17
                            color: 0.2, 0.2, 0.2, 1
                            halign: "left"
                            valign: "middle"
                            text_size: self.size

                        Label:
                            id: buero_rollladen_status
                            text: "OFFEN"
                            font_size: 11
                            bold: True
                            color: 1, 1, 1, 1
                            size_hint: (None, None)
                            size: (55, 25)
                            pos_hint: {"center_y": 0.5}
                            halign: "center"
                            valign: "middle"
                            canvas.before:
                                Color:
                                    rgba: (0.15, 0.65, 0.25, 1) if self.text == "OFFEN" else (0.8, 0.15, 0.15, 1)
                                RoundedRectangle:
                                    pos: self.pos
                                    size: self.size
                                    radius: [8]
                    
                        Label:
                            id: buero_rollladen_modus
                            text: "MANUELL"
                            font_size: 11
                            bold: True
                            color: 1, 1, 1, 1
                            size_hint: (None, None)
                            size: (65, 25)
                            pos_hint: {"center_y": 0.5}
                            halign: "center"
                            valign: "middle"
                            canvas.before:
                                Color:
                                    rgba: (0.8, 0.15, 0.15, 1) if self.text == "MANUELL" else (0.15, 0.65, 0.2, 1)
                                RoundedRectangle:
                                    pos: self.pos
                                    size: self.size
                                    radius: [8]
                    
                    #Schlafzimmer-Rollläden
                    BoxLayout:
                        orientation: "horizontal"
                        size_hint_y: None
                        height: 40
                        pos_hint: {"center_y": 0.5}
                
                        Label:
                            text: "Schlafzimmer"
                            font_size: 17
                            color: 0.2, 0.2, 0.2, 1
                            halign: "left"
                            valign: "middle"
                            text_size: self.size

                        Label:
                            id: schlafzimmer_rollladen_status
                            text: "OFFEN"
                            font_size: 11
                            bold: True
                            color: 1, 1, 1, 1
                            size_hint: (None, None)
                            size: (55, 25)
                            pos_hint: {"center_y": 0.5}
                            halign: "center"
                            valign: "middle"
                            canvas.before:
                                Color:
                                    rgba: (0.15, 0.65, 0.25, 1) if self.text == "OFFEN" else (0.8, 0.15, 0.15, 1)
                                RoundedRectangle:
                                    pos: self.pos
                                    size: self.size
                                    radius: [8]
                    
                        Label:
                            id: schlafzimmer_rollladen_modus
                            text: "MANUELL"
                            font_size: 11
                            bold: True
                            color: 1, 1, 1, 1
                            size_hint: (None, None)
                            size: (65, 25)
                            pos_hint: {"center_y": 0.5}
                            halign: "center"
                            valign: "middle"
                            canvas.before:
                                Color:
                                    rgba: (0.8, 0.15, 0.15, 1) if self.text == "MANUELL" else (0.15, 0.65, 0.2, 1)
                                RoundedRectangle:
                                    pos: self.pos
                                    size: self.size
                                    radius: [8]

                    #Platzhalter
                    Widget:

            #test
            #Sonnenstand    
            BoxLayout:
                orientation: "vertical"
                size_hint_y: None
                height: 110
                spacing: 2

                Label:
                    text: "Sonnenstand"
                    font_size: 22
                    bold: True
                    color: 0.15, 0.15, 0.15, 1
                    size_hint_y: None
                    height: 25
                    halign: "left"
                    text_size: self.size

                FloatLayout:
                    size_hint_y : None
                    height: 75
                        
                    SonnenVerlauf:
                        id: sonnen_bogen
                        size_hint: 1, 1
                        pos_hint: {"x": 0, "y": 0}
                    
                    Label:
                        id: sonnenaufgang_label
                        text: "--:--"
                        font_size: 14
                        color: 0.4, 0.4, 0.4, 1
                        size_hint: None, None
                        size: 50, 20
                        x: sonnen_bogen.center_x - 70 - self.width / 2
                        y: sonnen_bogen.y - 12

                    Label:
                        id: sonnenuntergang_label
                        text: "--:--"
                        font_size: 14
                        color: 0.4, 0.4, 0.4, 1
                        size_hint: None, None
                        size: 50, 20
                        x: sonnen_bogen.center_x + 70 - self.width / 2
                        y: sonnen_bogen.y - 12
                    
            Widget:
                size_hint_y: None
                height: 15

            #Anzeige für Aktivitäten (Queue)  
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
                    
            #Wohnzimmer-Licht Switches
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

            #Außenbeleuchtung
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
                    text: "Außenbeleuchtung"
                    font_size: 26
                    bold: True
                    color: 0.1,0.1,0.1,1

                    #Schalter fürs Licht umschalten
                Switch:
                    id: licht_switch_a
                    size_hint_y: None
                    height: 40
                    #Sperrt diesen Schalter, wenn Modus aktiv ist
                    disabled: modus_switch_a.active
                    #ruft bei klicken die Methode licht_schalten auf und übergibt True/False
                    on_active:                           
                        root.licht_schalten("außenbeleuchtung", self.active)

                Label:
                    id: licht_status_a
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
                    
        #Modus rechts unten:
        BoxLayout:
            orientation: "vertical"
            size_hint: (0.22, 0.15)
            pos_hint: {"right": 0.96, "y": 0.04}
            padding: 15
            spacing: 5
            canvas.before:
                Color:
                    rgba: 1, 1, 1, 1
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [20]

            Label:
                text: "Außen-Modus"
                font_size: 20
                bold: True
                color: 0.1, 0.1, 0.1, 1
                size_hint_y: 0.4
                    
            BoxLayout:
                orientation: "horizontal"
                size_hint_y: 0.6
                    
                Switch:
                    id: modus_switch_a
                    on_active: root.modus_schalten(self.active)
                
                Label:
                    id: modus_status_a
                    text: "Manuell"
                    font_size: 16
                    color: 0.35, 0.35, 0.35, 1
                    
<RollladenScreen>:
    canvas.before:
        Color:
            rgba: 0.95, 0.95, 0.95, 1
        Rectangle:
            pos: self.pos
            size: self.size
    
    FloatLayout:
        Label:
            text: "Rollladensteuerung"
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
                    
            #Wohnzimmer-Rollladen Switches
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

                    #Schalter für Rollladen umschalten
                Switch:
                    id: rollladen_switch_wz
                    size_hint_y: None
                    height: 40
                    disabled: modus_switch_ar.active
                    #ruft bei klicken die Methode rollladen_schalten auf und übergibt True/False
                    on_active:                           
                        root.rollladen_schalten("wohnzimmer", self.active)

                Label:
                    id: rollladen_status_wz
                    text: "Rollladen offen"
                    font_size: 18
                    color: 0.35,0.35,0.35,1

            #Küchen-Rollladen      
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

                    #Schalter für Rollladen umschalten
                Switch:
                    id: rollladen_switch_k
                    size_hint_y: None
                    height: 40
                    disabled: modus_switch_ar.active
                    #ruft bei klicken die Methode rollladen_schalten auf und übergibt True/False
                    on_active:                           
                        root.rollladen_schalten("kueche", self.active)

                Label:
                    id: rollladen_status_k
                    text: "Rollladen offen"
                    font_size: 18
                    color: 0.35,0.35,0.35,1

            #Büro-Rollladen
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

                    #Schalter für Rollladen umschalten
                Switch:
                    id: rollladen_switch_b
                    size_hint_y: None
                    height: 40
                    disabled: modus_switch_ar.active
                    #ruft bei klicken die Methode rollladen_schalten auf und übergibt True/False
                    on_active:                           
                        root.rollladen_schalten("buero", self.active)

                Label:
                    id: rollladen_status_b
                    text: "Rollladen offen"
                    font_size: 18
                    color: 0.35,0.35,0.35,1

            #Schlafzimmer-Rollladen
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

                    #Schalter für Rollladen umschalten
                Switch:
                    id: rollladen_switch_sz
                    size_hint_y: None
                    height: 40
                    disabled: modus_switch_ar.active
                    #ruft bei klicken die Methode rollladen_schalten auf und übergibt True/False
                    on_active:                           
                        root.rollladen_schalten("schlafzimmer", self.active)

                Label:
                    id: rollladen_status_sz
                    text: "Rollladen offen"
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
                    
        #Modus rechts unten:
        BoxLayout:
            orientation: "vertical"
            size_hint: (0.22, 0.15)
            pos_hint: {"right": 0.96, "y": 0.04}
            padding: 15
            spacing: 5
            canvas.before:
                Color:
                    rgba: 1, 1, 1, 1
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [20]

            Label:
                text: "Rollladen-Automatik"
                font_size: 20
                bold: True
                color: 0.1, 0.1, 0.1, 1
                size_hint_y: 0.4
                    
            BoxLayout:
                orientation: "horizontal"
                size_hint_y: 0.6
                    
                Switch:
                    id: modus_switch_ar
                    on_active: root.modus_schalten(self.active)
                
                Label:
                    id: modus_status_ar
                    text: "Manuell"
                    font_size: 16
                    color: 0.35, 0.35, 0.35, 1
                    
<SensorenScreen>:
    canvas.before:
        Color:
            rgba: 0.95, 0.95, 0.95, 1
        Rectangle:
            pos: self.pos
            size: self.size
    
    FloatLayout:
        Label:
            text: "Sensoren"
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
                    
            #Sensoren Anzeige
            #IDs werden in der Methode --- mit den echten APIs befüllt
            Label:
                text: "Sensoren:"
                font_size: 22
                bold: True
                color: 0.15,0.15,0.15,1
                size_hint: (0.2, 0.04)
                pos_hint: {"x": 0.67, "y": 0.22}

            Label:
                id: temp_label
                text: "---"
                font_size: 17
                color: 0.45, 0.45, 0.45, 1
                size_hint: (0.15, 0.03)
                pos_hint: {"x": 0.81, "y": 0.22}
                    
            Label:
                id: hum_label
                text: "---"
                font_size: 16
                color: 0.45, 0.45, 0.45, 1
                size_hint: (0.15, 0.03)
                pos_hint: {"x": 0.81, "y": 0.18}

            Label:
                id: press_label
                text: "---"
                font_size: 16
                color: 0.45, 0.45, 0.45, 1
                size_hint: (0.15, 0.03)
                pos_hint: {"x": 0.81, "y": 0.18}

            Label:
                id: light_label
                text: "---"
                font_size: 16
                color: 0.45, 0.45, 0.45, 1
                size_hint: (0.15, 0.03)
                pos_hint: {"x": 0.81, "y": 0.18}

            Label:
                id: rain_label
                text: "---"
                font_size: 16
                color: 0.45, 0.45, 0.45, 1
                size_hint: (0.15, 0.03)
                pos_hint: {"x": 0.81, "y": 0.18}

            #UV-Index
            Label:
                id: rain_label
                text: "---"
                font_size: 16
                color: 0.45, 0.45, 0.45, 1
                size_hint: (0.15, 0.03)
                pos_hint: {"x": 0.81, "y": 0.18}

            #UV reiner Wert
            Label:
                id: rain_label
                text: "---"
                font_size: 16
                color: 0.45, 0.45, 0.45, 1
                size_hint: (0.15, 0.03)
                pos_hint: {"x": 0.81, "y": 0.18}

            #so viele Label sinds gesamt  
            Label:
                id: rain_label
                text: "---"
                font_size: 16
                color: 0.45, 0.45, 0.45, 1
                size_hint: (0.15, 0.03)
                pos_hint: {"x": 0.81, "y": 0.18}
                    
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
                    
<WetterdatenScreen>:
    canvas.before:
        Color:
            rgba: 0.95, 0.95, 0.95, 1
        Rectangle:
            pos: self.pos
            size: self.size
    
    FloatLayout:
        Label:
            text: "Wetterdaten"
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

#test
class SonnenVerlauf(Widget):
    #Kivy Eigenschaften. Jede Änderung dieser Variablen aktualisiert automatisch die GUI
    prozent = NumericProperty(0.0)
    sonnen_x = NumericProperty(0)
    sonnen_y = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #Sorgt dafür dass die Sonne bei jeder Änderung automatisch mitwandert
        self.bind(pos=self.update_sonne, size=self.update_sonne, prozent=self.update_sonne)
        
    def update_sonne(self, *args):
        #Berechnet die XY-Koordinaten der Sonne auf der Kreisbahn
        radius = 70
        center_x = self.x + self.width / 2
        center_y = self.y + 10
        #rechnet den Tagesfortschritt (0% - 100%) in einen Kurvenwinkel
        winkel_deg = 180.0 - (self.prozent * 180.0)
        winkel_rad = math.radians(winkel_deg)
        #berechnet Position Sonne auf der Kurve (-10 zentriert den Sonnenkreis in mitte der Linie)
        self.sonnen_x = center_x + radius * math.cos(winkel_rad) - 10
        self.sonnen_y = center_y + radius * math.sin(winkel_rad) - 10


#Logik des ersten (Anmelde)-Bildschirm
class Login(Screen):
    def rfid_login(self):
        self.ids.status_label.text = "Status: Anmeldung erfolgreich"        #Verknüpfung Kv-String
        App.get_running_app().log_event("User eingeloggt mit RFID")         #Queue
        self.manager.current = "loading"                                    #schaltet ScreenManager auf Ladebildschirm um
        self.manager.transition.direction = "left"



"""Weiß noch nicht ob drinlassen?!"""
#Vorerst nur zum testen von GIF
#Logik des (Lade)-Bildschirms
class LadeBildschirm(Screen):
    def on_enter(self):
        Clock.schedule_once(self.wechseln, 2)           #Verzögerung 2 Sekunden (Ladevorgang), dann self.wechseln
    
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

        #Aktualisiert jede Sekunde die Uhrzeit
        Clock.schedule_interval(self.update_uhrzeit, 1.0)
        #erstellt Kivy Dropdown im Hintergrund
        self.dropdown = DropDown()
        self.dropdown.background_color = (0, 0, 0, 0)
        self.dropdown.background_normal = ""
        self.dropdown.container.spacing = 4
        self.dropdown.container.padding = [0, 8, 0, 0]
        
        punkte = [
            "Licht",
            "Rollläden",
            "Sensoren",
            "Wetterdaten",
            "Sonstiges"
        ]

        #Schleife für die Buttons des Dropdown-Menüs
        for punkt in punkte:
            btn = Factory.DropdownButton(text=punkt)
            #ruft beim klicken auf einen Punkt des Dropdowns self.menu_aktion auf. Lambda sorgt für, dass der spezifische Text des Buttons beim Klick übergeben wird
            btn.bind(on_release=lambda x: self.menu_aktion(x.text))
            self.dropdown.add_widget(btn)

    def lade_wetter(self, dt=0):
        #Koordinaten für OpenWeatherMap-Abfrage (Bopfingen)
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

                #test
                #Sonnenverlauf berechnen
                jetzt = int(time.time()) # Aktuelle Systemzeit in Sekunden
                sonnenaufgang = data["city"]["sunrise"]
                sonnenuntergang = data["city"]["sunset"]
                aufgang_uhrzeit = datetime.fromtimestamp(sonnenaufgang).strftime("%H:%M")
                untergang_uhrzeit = datetime.fromtimestamp(sonnenuntergang).strftime("%H:%M")

                #Prozentuale Position der Sonne
                if jetzt < sonnenaufgang:
                    prozent = 0.0 # Sonne ist noch nicht aufgegangen
                elif jetzt > sonnenuntergang:
                    prozent = 1.0 # Sonne ist bereits untergegangen
                else:
                    gesamtdauer = sonnenuntergang - sonnenaufgang
                    vergangen = jetzt - sonnenaufgang
                    prozent = vergangen / gesamtdauer

                # Übergebe die Prozentzahl an Kivy GUI
                self.ids.sonnen_bogen.prozent = prozent
                self.ids.sonnenaufgang_label.text = aufgang_uhrzeit
                self.ids.sonnenuntergang_label.text = untergang_uhrzeit

                #Kleidungsempfehlung mit Temperatur, darunter Zusatzbedingungen
                if temperatur <= 0:
                    empfehlung = "Winterjacke, Mütze und Handschuhe enmpfohlen"
                elif temperatur <= 10:
                    empfehlung = "Warme Jacke empfohlen"
                elif temperatur <= 16:
                    empfehlung = "Pullover oder leichte Jacke"
                elif temperatur <= 21:
                    empfehlung = "T-Shirt oder dünner Pullover"
                else:
                    empfehlung = "Kurze Kleidung empfohlen"

                wetter_überprüfen = wetter.lower()

                if "regen" in wetter_überprüfen or "schauer" in wetter_überprüfen:
                    empfehlung += ", Regenschirm mitnehmen"
                elif "gewitter" in wetter_überprüfen:
                    empfehlung += ", VORSICHT Gewitter!"
                elif "schnee" in wetter_überprüfen:
                    empfehlung += ", Winterkleidung empfohlen!"
                elif "nebel" in wetter_überprüfen:
                    empfehlung += ", schlechte Sicht!"
                
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
        #zeigt Popup Willkommen einmalig
        if self.popup_anzeigen:
            popup = Popup(
                title="Info",
                content=Label(text="Willkommen"),
                size_hint=(None, None),
                size=(300, 200)
            )
            popup.open()
            #Schließt automatisch nach 2 Sekunden
            Clock.schedule_once(lambda dt: popup.dismiss(), 2)
            self.popup_anzeigen = False
            
        #erst kurz nach dem Laden der Seite werden Wetterdaten aktualisiert, sonst Fehler WICHTIG!!!
        Clock.schedule_once(self.lade_wetter, 0.1)
    
    def menu_aktion(self, text):
        #Klicks auf dem Dropdown (Bildschirmwechsel)
        self.dropdown.dismiss()     #schließt Dropdown
        if text == "Licht":
            self.manager.current = "licht"
            self.manager.transition.direction = "left"
        elif text == "Rollläden":
            self.manager.current = "rollladen"
            self.manager.transition.direction = "left"
        elif text == "Sensoren":
            self.manager.current = "sensoren"
            self.manager.transition.direction = "left"
        elif text == "Wetterdaten":
            self.manager.current = "wetterdaten"
            self.manager.transition.direction = "left"

    def update_uhrzeit(self, *args):
        #Livelabel
        wochentage = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
        jetzt = datetime.now()
        tag_name = wochentage[jetzt.weekday()]
        datum = jetzt.strftime("%d.%m.%Y")
        uhrzeit = jetzt.strftime("%H:%M:%S")

        anzeige_text = f"{tag_name}, {datum}, {uhrzeit}"

        if "live_zeit_label" in self.ids:
            self.ids.live_zeit_label.text = anzeige_text

    popup_anzeigen = False

#Schalter für die Beleuchtung
class LichtScreen(Screen):
    def licht_schalten(self, raum, status):
        steuerung = self.manager.get_screen("Smart-Home")
        app = App.get_running_app()
        
        #Zeigt den neuen Status auf der GUI an undspeichert den Text im Verlauf
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
        elif raum == "außenbeleuchtung":
            self.ids.licht_status_a.text = "Licht eingeschaltet" if status else "Licht ausgeschaltet"
            steuerung.ids.außenbeleuchtung_licht_status.text = "EIN" if status else "AUS"
            app.log_event(f"Außenbeleuchtung Licht {'AN' if status else 'AUS'}")

        # Befehl via App-Klasse an den Pico senden
        status_wert = "1" if status else "0"
        app.sende_an_pico(f"{raum}:{status_wert}")

    def modus_schalten(self, is_auto):
        steuerung = self.manager.get_screen("Smart-Home")
        app = App.get_running_app()

        if is_auto:
            self.ids.modus_status_a.text = "Automatik"
            steuerung.ids.außenbeleuchtung_modus_status.text = "AUTO"
            app.log_event("Außenlicht: Modus Automatik")
        else:
            self.ids.modus_status_a.text = "MANUELL"
            steuerung.ids.außenbeleuchtung_modus_status.text = "MANUELL"
            app.log_event("Außenbeleuchtung: Modus Manuell")

#Schalter für die Rollläden
class RollladenScreen(Screen):
    def rollladen_schalten(self, raum, status):
        steuerung = self.manager.get_screen("Smart-Home")
        #status liefert True oder False vom Kivy-Switch
        if raum == "wohnzimmer":
            if status:
                self.ids.rollladen_status_wz.text = "Rollladen geschlossen" 
                steuerung.ids.wohnzimmer_rollladen_status.text = "ZU"      #ändert Text live
                App.get_running_app().log_event("Wohnzimmer Rollladen geschlossen")  #Queue
            else:
                self.ids.rollladen_status_wz.text = "Rollladen geöffnet"
                steuerung.ids.wohnzimmer_rollladen_status.text = "OFFEN"      #ändert Text live
                App.get_running_app().log_event("Wohnzimmer Rollladen geöffnet")  #Queue
        elif raum == "kueche":
            if status:
                self.ids.rollladen_status_k.text = "Rollladen geschlossen"
                steuerung.ids.kueche_rollladen_status.text = "ZU"
                App.get_running_app().log_event("Küche Rollladen geschlossen")  #Queue
            else:
                self.ids.rollladen_status_k.text = "Rollladen geöffnet"
                steuerung.ids.kueche_rollladen_status.text = "OFFEN"
                App.get_running_app().log_event("Küche Rollladen geöffnet")  #Queue
        elif raum == "buero":
            if status:
                self.ids.rollladen_status_b.text = "Rollladen geschlossen"
                steuerung.ids.buero_rollladen_status.text = "ZU"
                App.get_running_app().log_event("Büro Rollladen geschlossen")  #Queue
            else:
                self.ids.rollladen_status_b.text = "Rollladen geöffnet"
                steuerung.ids.buero_rollladen_status.text = "OFFEN"
                App.get_running_app().log_event("Büro Rollladen geöffnet")  #Queue
        elif raum == "schlafzimmer":
            if status:
                self.ids.rollladen_status_sz.text = "Rollladen geschlossen"
                steuerung.ids.schlafzimmer_rollladen_status.text = "ZU"
                App.get_running_app().log_event("Schlafzimmer Rollladen gschlossen")  #Queue
            else:
                self.ids.rollladen_status_sz.text = "Rollladen geöffnet"
                steuerung.ids.schlafzimmer_rollladen_status.text = "OFFEN"
                App.get_running_app().log_event("Schlafzimmer Rollladen geöffnet")  #Queue

    def modus_schalten(self, is_auto):
        steuerung = self.manager.get_screen("Smart-Home")
        app = App.get_running_app()

        if is_auto:
            self.ids.modus_status_ar.text = "Automatik"
            steuerung.ids.wohnzimmer_rollladen_modus.text = "AUTO"
            steuerung.ids.kueche_rollladen_modus.text = "AUTO"
            steuerung.ids.buero_rollladen_modus.text = "AUTO"
            steuerung.ids.schlafzimmer_rollladen_modus.text = "AUTO"
            app.log_event("Rollladen: Modus Automatik")
        else:
            self.ids.modus_status_ar.text = "Manuell"
            steuerung.ids.wohnzimmer_rollladen_modus.text = "MANUELL"
            steuerung.ids.kueche_rollladen_modus.text = "MANUELL"
            steuerung.ids.buero_rollladen_modus.text = "MANUELL"
            steuerung.ids.schlafzimmer_rollladen_modus.text = "MANUELL"
            app.log_event("Rollladen: Modus Manuell")

#Sensoren Screen, um eigene Sensordaten anzeigen zu lassen
class SensorenScreen(Screen):
    pass

#Wetterdaten Screen, um alle spezifischere, mehr Daten anzeigen zu lassen
class WetterdatenScreen(Screen):
    def wetterdaten(self, umweltdaten, regendaten, lichtdaten):
        steuerung = self.manager.get_screen("Smart-Home")
                                  

ms = ScreenManager()
#Fügt die Bildschirme dem Manager zu
ms.add_widget(Login(name="login"))
ms.add_widget(LadeBildschirm(name="loading"))
ms.add_widget(Steuerung(name="Smart-Home"))
ms.add_widget(LichtScreen(name="licht"))
ms.add_widget(RollladenScreen(name="rollladen"))
ms.add_widget(SensorenScreen(name="sensoren"))
ms.add_widget(WetterdatenScreen(name="wetterdaten"))
    
class StartApp(App):
    title = "HS Smart-Home"
    #Datenstruktur, bei maxlen=3 ältester Eintrag fliegt raus
    aktivitaeten_queue = deque(maxlen=3)        #max 3 Einträge

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ser = None
        #Verbindung RaspberryPi Pico. WICHTIG: COM5 bei Sebi Laptop!
        try:
            self.ser = serial.Serial(port='COM5', baudrate=115200, timeout=1)
            time.sleep(1) # Kurze Pause für den Verbindungsaufbau
            print("Verbindung zum Pico erfolgreich hergestellt!")
        except Exception as e:
            print(f"WARNUNG: Konnte Verbindung zum Pico nicht öffnen: {e}")

    def sende_an_pico(self, befehl):
        #Übermittelt Befehle per USB-Serial, falls die Verbindung offen ist'
        if self.ser and self.ser.is_open:
            try:
                # Wichtig: CircuitPython braucht das '\n'
                self.ser.write(f"{befehl}\n".encode('utf-8'))
            except Exception as e:
                print(f"Fehler beim Senden an Pico: {e}")
        else:
            print(f"Pico nicht verbunden. Befehl '{befehl}' wurde verworfen.")

    def read_data(self, dt):
        if self.ser and self.ser.in_waiting:
            zeile = self.ser.readline().decode().strip()

            try:
                msg = json.loads(zeile)

                if msg["type"] != "sensor":
                    return
                
                daten = msg["data"]

                temp = daten["Umweltsensor"]["Temperatur"]
                hum = daten["Umweltsensor"]["Luftfeuchtigkeit"]
                druck = daten["Umweltsensor"]["Luftdruck"]
                licht = daten["Lichtsensor"]["ambient"]
                regen = daten["Regensensor"]["Regen"]

                sensor_screen = self.root.get_screen("sensoren")

                sensor_screen.ids.temp_label.text = f"{temp} °C"
                sensor_screen.ids.hum_label.text = f"{hum} %"
                sensor_screen.ids.press_label.text = f"{druck} hPa"
                sensor_screen.ids.light_label.text = str(licht)
                sensor_screen.ids.rain_label.text = "Ja" if regen else "Nein"

            except Exception as e:
                print(e)

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
        Clock.schedule_interval(self.read_data, 1.0)
        return ms           #Startet die App
    
if __name__ == "__main__":
    StartApp().run()