import speech_recognition as sr
import pyttsx3
import paho.mqtt.client as mqtt
import sys
import datetime
import time
import requests
import json
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

sys.stdout.reconfigure(encoding='utf-8')

# Configurações do MQTT
mqtt_server = "192.168.15.10"
mqtt_port = 1883
mqtt_user = "RobsonBrasil"
mqtt_password = "loboalfa"

# Tópicos MQTT para os relés
relay_topics = [
    "ESP32/MinhaCasa/QuartoRobson/Interruptor1/Comando",
    "ESP32/MinhaCasa/QuartoRobson/Interruptor2/Comando",
    "ESP32/MinhaCasa/QuartoRobson/Interruptor3/Comando",
    "ESP32/MinhaCasa/QuartoRobson/Interruptor4/Comando",
    "ESP32/MinhaCasa/QuartoRobson/Interruptor5/Comando",
    "ESP32/MinhaCasa/QuartoRobson/Interruptor6/Comando",
    "ESP32/MinhaCasa/QuartoRobson/Interruptor7/Comando",
    "ESP32/MinhaCasa/QuartoRobson/Interruptor8/Comando",
    "ESP32/MinhaCasa/QuartoRobson/Temperatura"
]

# Dicionário de aliases para os tópicos
topic_aliases = {
    "ESP32/MinhaCasa/QuartoRobson/Interruptor1/Comando": "lâmpada forte",
    "ESP32/MinhaCasa/QuartoRobson/Interruptor2/Comando": "lâmpada fraca",
    "ESP32/MinhaCasa/QuartoRobson/Interruptor3/Comando": "cooler",
    "ESP32/MinhaCasa/QuartoRobson/Interruptor4/Comando": "relé 4",
    "ESP32/MinhaCasa/QuartoRobson/Interruptor5/Comando": "relé 5",
    "ESP32/MinhaCasa/QuartoRobson/Interruptor6/Comando": "relé 6",
    "ESP32/MinhaCasa/QuartoRobson/Interruptor7/Comando": "relé 7",
    "ESP32/MinhaCasa/QuartoRobson/Interruptor8/Comando": "refletor",
    "ESP32/MinhaCasa/QuartoRobson/Temperatura": "ambiente"
}

class KivyApp(App):
    
    def build(self):
        layout = BoxLayout(orientation='vertical')
        button = Button(text='Clique para falar')
        button.bind(on_press=self.falar_comando)
        layout.add_widget(button)
        self.label = Label(text='')
        layout.add_widget(self.label)

        return layout

    def falar(self, audio):
        rate =  self.texto_fala.getProperty('rate')
        self.texto_fala.setProperty('rate', 180)
        voices = self.texto_fala.getProperty('voices')
        self.texto_fala.setProperty('voice', voices[3].id)  # Trocar as vozes
        self.texto_fala.say(audio)
        self.texto_fala.runAndWait()
        time.sleep(0.5)  # Adiciona uma pausa de 0,5 segundos após cada fala

    def hora(self):
        Hora = datetime.datetime.now().strftime("%#H horas e,:%#M minutos,")
        self.falar("Agora são,")
        self.falar(Hora)

    def obter_nome_mes(self, numero_mes):
        
        meses = {
            
            1: "Janeiro!",
            2: "Fevereiro!",
            3: "Março!",
            4: "Abril!",
            5: "Maio!",
            6: "Junho,",
            7: "Julho!",
            8: "Agosto!",
            9: "Setembro!",
            10: "Outubro!",
            11: "Novembro!",
            12: "Dezembro!"
        }
        return meses.get(numero_mes, "Mês inválido")

    def data(self):
        now = datetime.datetime.now()
        dia = str(now.day)
        mes = self.obter_nome_mes(now.month)
        ano = str(now.year)

        self.falar("A data de hoje é....," + dia,)
        self.falar("de-----,   " + mes,)
        self.falar("de----- ,  " + ano,)

    def bem_vindo(self):
        self.falar("Olá Robson Brasil, seja bem-vindo de volta,")
        self.hora()
        self.data()

    periodo_do_dia = datetime.datetime.now().hour

    if periodo_do_dia >= 6 and periodo_do_dia < 12:
        self.falar("Bom dia mestre,")
    elif periodo_do_dia >= 12 and periodo_do_dia < 18:
        self.falar("Boa tarde mestre,")
    elif periodo_do_dia >= 18 and periodo_do_dia <= 24:
        self.falar("Boa noite mestre,")
    else:
        self.falar("Mestre, vá dormir, já é de madrugada!,")
    
    self.falar("Jarvis à sua disposição! Diga-me como posso ajudá-lo hoje?,")

    def on_message(self, client, userdata, message):
        global assistant_active
        payload = message.payload.decode("utf-8")

        client.on_message = self.on_message

        client.subscribe("voiceAssistant/enable")
        client.subscribe("voiceAssistant/voice")
        client.loop_forever()

    def microfone(self):
        r = sr.Recognizer()

        with sr.Microphone() as source:
            r.pause_threshold = 1
            audio = r.listen(source)

        try:
            print("Reconhecendo o Comando")
            command = r.recognize_google(audio, language='pt-BR')
            print(command)

        except Exception as e:
            print(e)
            # falar(" Por favor Repita, não entendi,")
            return "None"

        return command

    def falar_comando(self, instance):
        
        command = self.microfone().lower()
        
    if 'como você está' in command:
        self.falar("Estou bem, obrigado e você,")
        self.falar("o que posso fazer para ajudá-lo mestre,")

    elif 'hora' in command:
        self.hora()

    elif 'data' in command:
        self.data()

    elif 'ligar' in command:
    if 'lâmpada forte' in command:
        self.publicar_mqtt("ESP32/MinhaCasa/QuartoRobson/Interruptor1/Comando", "Ligar")
    elif 'lâmpada fraca' in command:
        self.publicar_mqtt("ESP32/MinhaCasa/QuartoRobson/Interruptor2/Comando", "Ligar")
    elif 'cooler' in command:
        self.publicar_mqtt("ESP32/MinhaCasa/QuartoRobson/Interruptor3/Comando", "Ligar")
    elif 'relé 4' in command:
        self.publicar_mqtt("ESP32/MinhaCasa/QuartoRobson/Interruptor4/Comando", "Ligar")
    elif 'relé 5' in command:
        self.publicar_mqtt("ESP32/MinhaCasa/QuartoRobson/Interruptor5/Comando", "Ligar")
    elif 'relé 6' in command:
        self.publicar_mqtt("ESP32/MinhaCasa/QuartoRobson/Interruptor6/Comando", "Ligar")
    elif 'relé 7' in command:
        self.publicar_mqtt("ESP32/MinhaCasa/QuartoRobson/Interruptor7/Comando", "Ligar")
    elif 'refletor' in command:
        self.publicar_mqtt("ESP32/MinhaCasa/QuartoRobson/Interruptor8/Comando", "Ligar")
    else:
        self.falar("Desculpe, não reconheci o dispositivo para ligar.")

    elif 'desligar' in command:
    if 'lâmpada forte' in command:
        self.publicar_mqtt("ESP32/MinhaCasa/QuartoRobson/Interruptor1/Comando", "Desligar")
    elif 'lâmpada fraca' in command:
        self.publicar_mqtt("ESP32/MinhaCasa/QuartoRobson/Interruptor2/Comando", "Desligar")
    elif 'cooler' in command:
        self.publicar_mqtt("ESP32/MinhaCasa/QuartoRobson/Interruptor3/Comando", "Desligar")
    elif 'relé 4' in command:
        self.publicar_mqtt("ESP32/MinhaCasa/QuartoRobson/Interruptor4/Comando", "Desligar")
    elif 'relé 5' in command:
        self.publicar_mqtt("ESP32/MinhaCasa/QuartoRobson/Interruptor5/Comando", "Desligar")
    elif 'relé 6' in command:
        self.publicar_mqtt("ESP32/MinhaCasa/QuartoRobson/Interruptor6/Comando", "Desligar")
    elif 'relé 7' in command:
        self.publicar_mqtt("ESP32/MinhaCasa/QuartoRobson/Interruptor7/Comando", "Desligar")
    elif 'refletor' in command:
        self.publicar_mqtt("ESP32/MinhaCasa/QuartoRobson/Interruptor8/Comando", "Desligar")
    else:
        self.falar("Desculpe, não reconheci o dispositivo para desligar.")

    elif 'temperatura' in command:
        self.publicar_mqtt("ESP32/MinhaCasa/QuartoRobson/Temperatura", "Obter")
    elif 'ajuda' in command:
        self.falar("Você pode me pedir para fazer várias coisas, como:")
        self.falar("- Perguntar a hora")
        self.falar("- Perguntar a data")
        self.falar("- Ligar ou desligar dispositivos, como lâmpadas, cooler e relés")
        self.falar("- Obter a temperatura do ambiente")
        self.falar("Experimente fazer alguns comandos!")
    else:
        self.falar("Desculpe, não entendi o comando. Por favor, repita.")

    def publicar_mqtt(self, topic, message):
        client = mqtt.Client()
        client.username_pw_set(mqtt_user, mqtt_password)
        client.connect(mqtt_server, mqtt_port, 60)
        client.publish(topic, message)
        client.disconnect()

    def on_start(self):
        self.texto_fala = pyttsx3.init()
        self.texto_fala.setProperty('rate', 180)
        self.texto_fala.setProperty('voice', self.texto_fala.getProperty('voices')[3].id)
        self.bem_vindo()

    def on_stop(self):
        self.texto_fala.stop()

if __name__ == '__main__':
KivyApp().run()