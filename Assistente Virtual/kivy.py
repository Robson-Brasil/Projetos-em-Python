from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
import speech_recognition as sr
import pyttsx3
import paho.mqtt.client as mqtt


class MainApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mqtt_server = "192.168.15.10"
        self.mqtt_port = 1883
        self.mqtt_user = "RobsonBrasil"
        self.mqtt_password = "loboalfa"
        self.relay_topics = [
            "ESP32/MinhaCasa/QuartoRobson/Interruptor1/Comando",
            "ESP32/MinhaCasa/QuartoRobson/Interruptor2/Comando",
            "ESP32/MinhaCasa/QuartoRobson/Interruptor3/Comando",
            "ESP32/MinhaCasa/QuartoRobson/Interruptor4/Comando",
            "ESP32/MinhaCasa/QuartoRobson/Interruptor5/Comando",
            "ESP32/MinhaCasa/QuartoRobson/Interruptor6/Comando",
            "ESP32/MinhaCasa/QuartoRobson/Interruptor7/Comando",
            "ESP32/MinhaCasa/QuartoRobson/Interruptor8/Comando",
        ]
        self.topic_aliases = {
            "ESP32/MinhaCasa/QuartoRobson/Interruptor1/Comando": "luz forte",
            "ESP32/MinhaCasa/QuartoRobson/Interruptor2/Comando": "luz fraca",
            "ESP32/MinhaCasa/QuartoRobson/Interruptor3/Comando": "cooler",
            "ESP32/MinhaCasa/QuartoRobson/Interruptor4/Comando": "relé 4",
            "ESP32/MinhaCasa/QuartoRobson/Interruptor5/Comando": "relé 5",
            "ESP32/MinhaCasa/QuartoRobson/Interruptor6/Comando": "relé 6",
            "ESP32/MinhaCasa/QuartoRobson/Interruptor7/Comando": "relé 7",
            "ESP32/MinhaCasa/QuartoRobson/Interruptor8/Comando": "luz do quarto",
        }
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.client = mqtt.Client()
        self.assistant_active = True

    def build(self):
        layout = BoxLayout(orientation="vertical")

        label = Label(text="Ouvindo...")
        layout.add_widget(label)

        button = Button(text="Parar Assistente")
        button.bind(on_press=self.toggle_assistant)
        layout.add_widget(button)

        Clock.schedule_interval(self.listen_and_execute, 1)

        self.client.username_pw_set(self.mqtt_user, self.mqtt_password)
        self.client.connect(self.mqtt_server, self.mqtt_port, 60)
        self.client.on_message = self.on_message
        self.client.subscribe("voiceAssistant/enable")
        self.client.subscribe("voiceAssistant/voice")
        self.client.loop_start()

        return layout

    def toggle_assistant(self, instance):
        if self.assistant_active:
            self.assistant_active = False
            instance.text = "Iniciar Assistente"
        else:
            self.assistant_active = True
            instance.text = "Parar Assistente"

    def on_message(self, client, userdata, message):
        payload = message.payload.decode("utf-8")
        if message.topic == "voiceAssistant/enable":
            if payload == "2":
                self.assistant_active = True
            else:
                self.assistant_active = True

        if message.topic == "voiceAssistant/voice":
            self.engine.setProperty("voice", payload)

    def listen_and_execute(self, dt):
        if self.assistant_active:
            with sr.Microphone() as source:
                print("Ouvindo...")
                audio = self.recognizer.listen(source)

            try:
                command = self.recognizer.recognize_google(audio, language='pt-BR')
                print(f"Você disse: {command}")
                self.process_command(command)
            except sr.UnknownValueError:
                print("Não entendi, por favor repita.")
            except sr.RequestError:
                print("Erro ao tentar reconhecer o comando.")

    def process_command(self, command):
        command = command.lower()

        for i, topic in enumerate(self.relay_topics):
            alias = self.topic_aliases[topic]
            if f"ligar {alias}" in command:
                self.client.publish(topic, "1")
                self.engine.say(f"Ligando o {alias}.")
                self.engine.runAndWait()
                return

            if f"apagar {alias}" in command:
                self.client.publish(topic, "0")
                self.engine.say(f"Apagando o {alias}")
                self.engine.runAndWait()
                return

        self.engine.say("Comando não reconhecido.")
        self.engine.runAndWait()


if __name__ == "__main__":
    MainApp().run()