import speech_recognition as sr
import pyttsx3
import paho.mqtt.client as mqtt
import sys
import datetime

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

    # falar
texto_fala = pyttsx3.init()

def falar(audio):
    rate =  texto_fala.getProperty('rate')
    texto_fala.setProperty('rate', 120)
    voices = texto_fala.getProperty('voices')
    texto_fala.setProperty('voice', voices[3].id) # Trocar as vozes
    texto_fala.say(audio)
    texto_fala.runAndWait()
    
def hora():
    Hora = datetime.datetime.now().strftime("%H horas e,:%#M minutos,")
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
    
    falar("A data atual é,...." + dia,)
    falar("de-----,   " + mes,)
    falar("de----- ,  " + ano,)

def bem_vindo():
    falar ("Olá mestre, seja bem vindo de volta,")
    hora()
    data()
    
    periodo_do_dia = datetime.datetime.now().hour
    
    if periodo_do_dia >= 6 and periodo_do_dia < 12:
        falar ("Bom dia mestre,")
    elif periodo_do_dia >= 12 and periodo_do_dia < 18:
        falar ("Boa tarde mestre,")
    elif periodo_do_dia >= 18 and periodo_do_dia <= 24:
        falar ("Boa noite mestre,")
        falar("Jarvis a sua disposição! Diga-me como posso ajudá-lo hoje?,")
    else:
        falar("Mestre, vá dormir, já é de madrugada!,")

assistant_active = True

def on_message(client, userdata, message):
    global assistant_active
    payload = message.payload.decode("utf-8")

    client.on_message = on_message
    client.subscribe("voiceAssistant/enable")
    client.subscribe("voiceAssistant/voice")
    client.loop_start()

def microfone():
    r = sr.Recognizer()
    
    with sr.Microphone() as source:
        r.pause_threshold = 1
        audio = r.listen(source)
    
    try:
        print("Reconhecendo o command")
        command = r.recognize_google(audio, language='pt-BR')
        print(command)

    except Exception as e:
        print(e)
        falar(" Por favor Repita, não entendi,")
        
        return "None"
    
    return command

# Configurar o cliente MQTT
client = mqtt.Client()
client.username_pw_set(mqtt_user, mqtt_password)
client.connect(mqtt_server, mqtt_port, 60)

def process_command(command):
    command = command.lower()

    for i, topic in enumerate(relay_topics):
        alias = topic_aliases[topic]
        if f"acender {alias}" in command:
            client.publish(topic, "1")
            engine.say(f"Ligando o {alias}")
            engine.runAndWait()
            return

        if f"apagar {alias}" in command:
            client.publish(topic, "0")
            engine.say(f"Apagando o {alias}")
            engine.runAndWait()
            return

    falar ("command não reconhecido.")
    engine.runAndWait()

if __name__ == "__main__":
    bem_vindo()
    
    while True:
        print("Estou Escutando....")
        if assistant_active:
            command = microfone().lower()
        
        if 'como você está' in command:
            falar("Estou bem, obrigado e você,")
            falar("o que posso fazer para ajudá-lo mestre,")
        
        elif 'hora' in command:
            hora()

        elif 'data' in command:
            data()
        
        for topic in relay_topics:    
            alias = topic_aliases[topic]
            if f"acender {alias}" in command:
                client.publish(topic, "1")
                falar(f"Ligando o {alias}")

            elif f"apagar {alias}" in command:
                client.publish(topic, "0")
                falar(f"Apagando o {alias}")
