import pyttsx3
import paho.mqtt.client as mqtt
import sys
import datetime
import time
import requests
import json
from vosk import Model, KaldiRecognizer
import pyaudio
import wave

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

# Create the PyAudio stream and Vosk recognizer objects
audio = pyaudio.PyAudio()
stream = audio.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
model = Model("D:\GitRepositorio\Projetos-em-Python\Jarvis-Vosk\model")
recognizer = KaldiRecognizer(model, 16000)

def falar(audio):
    texto_fala = pyttsx3.init()
    rate = texto_fala.getProperty('rate')
    texto_fala.setProperty('rate', 180)
    voices = texto_fala.getProperty('voices')
    texto_fala.setProperty('voice', voices[3].id)

    while True:
        # Read data from the audio stream
        data = stream.read(16000, exception_on_overflow=False)

        # Feed the data to the Vosk recognizer
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            comando = result['text'].lower()
            print(comando)
            break

def hora():
    Hora = datetime.datetime.now().    strftime("%#H horas e,:%#M minutos,")
    falar("Agora são,")
    falar(Hora)

def obter_nome_mes(numero_mes):
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

def data():
    now = datetime.datetime.now()
    dia = str(now.day)
    mes = obter_nome_mes(now.month)
    ano = str(now.year)

    falar("A data de hoje é....," + dia, )
    falar("de-----,   " + mes, )
    falar("de----- ,  " + ano, )

def bem_vindo():
    falar("Olá Robson Brasil, seja bem-vindo de volta,")
    hora()
    data()

    periodo_do_dia = datetime.datetime.now().hour

    if periodo_do_dia >= 6 and periodo_do_dia < 12:
        falar("Bom dia mestre,")
    elif periodo_do_dia >= 12 and periodo_do_dia < 18:
        falar("Boa tarde mestre,")
    elif periodo_do_dia >= 18 and periodo_do_dia <= 24:
        falar("Boa noite mestre,")
    else:
        falar("Mestre, vá dormir, já é de madrugada!,")

assistant_active = True

def on_message(client, userdata, message):
    global assistant_active
    payload = message.payload.decode("utf-8")
    client.on_message = on_message
    client.subscribe("voiceAssistant/enable")
    client.subscribe("voiceAssistant/voice")
    client.loop_forever()

def microfone():
    # Create the PyAudio stream and Vosk recognizer objects before using them in falar() function
    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
    model = Model("model")
    recognizer = KaldiRecognizer(model, 16000)

    print("Escutando...")

    return "None"

# Configurar o cliente MQTT

client = mqtt.Client()
client.username_pw_set(mqtt_user, mqtt_password)
client.connect(mqtt_server, mqtt_port, 60)

if __name__ == "__main__":
    bem_vindo()

    while True:
        # Read audio data from the stream
        data = stream.read(8000, exception_on_overflow=True)

        # Feed the data to the Vosk recognizer
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            comando = result['text'].lower()
            print(comando)

            if 'como você está' in comando:
                falar("Estou bem, obrigado. E você?")
                falar("O que posso fazer para ajudá-lo, mestre?")
            elif 'hora' in comando:
                hora()
            elif 'data' in comando:
                data()

            for topic in relay_topics:
                alias = topic_aliases[topic]

                if f"acender {alias}" in comando:
                    client.publish(topic, "1")
                    falar(f"Ligando o {alias}")
                elif f"apagar {alias}" in comando:
                    client.publish(topic, "0")
                    falar(f"Apagando o {alias}")
