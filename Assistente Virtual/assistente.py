import speech_recognition as sr
import pyttsx3
import paho.mqtt.client as mqtt

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
    "ESP32/MinhaCasa/QuartoRobson/Interruptor8/Comando": "refletor"
}

# Configurar o reconhecimento de voz
recognizer = sr.Recognizer()

# Configurar a síntese de voz
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('rate', 180)  # velocidade 120 = lento

for indice in range(len(voices)):  # listar vozes
    print(f"Voz {indice}: {voices[indice].id}")

# ouvir
    r = sr.Recognizer()
    mic = sr.Microphone()

# Configurar o cliente MQTT
client = mqtt.Client()
client.username_pw_set(mqtt_user, mqtt_password)
client.connect(mqtt_server, mqtt_port, 60)

assistant_active = True

def on_message(client, userdata, message):
    global assistant_active
    payload = message.payload.decode("utf-8")

    if message.topic == "voiceAssistant/enable":
        if payload == "3":
            assistant_active = False
        else:
            assistant_active = True  # Corrected the indexing error here

    if message.topic == "voiceAssistant/voice":
        voice_index = config_assistente["voz"]  # Convert payload to an integer
        if voice_index < len(voices):
            engine.setProperty('voice', voices[voice_index].id)
            engine.say(texto)
            engine.runAndWait()
            engine.stop()
        else:
            print("Invalid voice index")

client.on_message = on_message
client.subscribe("voiceAssistant/enable")
client.subscribe("voiceAssistant/voice")
client.loop_start()

def listen_and_execute():
    with sr.Microphone() as source:
        r.pause_threshold = 100
        print("Ouvindo...")
        audio = recognizer.listen(source)
        
    try:
        command = recognizer.recognize_google(audio, language='pt-BR')
        print(f"Você disse: {command}")
        process_command(command)
        
    except sr.UnknownValueError:
        print("Não entendi, por favor repita.")
        engine.say("Não entendi, por favor repita.")
        
    except sr.RequestError:
        print("Erro ao tentar reconhecer o comando.")
        engine.say("Erro ao tentar reconhecer o comando.")

def process_command(command):
    command = command.lower()

    for i, topic in enumerate(relay_topics):
        alias = topic_aliases[topic]
        if f"acender {alias}" in command:
            client.publish(topic, "1")
            engine.say(f"Ligando o {alias}.")
            engine.runAndWait()
            return

        if f"apagar {alias}" in command:
            client.publish(topic, "0")
            engine.say(f"Apagando o {alias}")
            engine.runAndWait()
            return

    engine.say("Comando não reconhecido.")
    engine.runAndWait()

while True:
    if assistant_active:
        listen_and_execute()