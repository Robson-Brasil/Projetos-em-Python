import speech_recognition as sr
import pyttsx3
import paho.mqtt.client as mqtt
import sys
import datetime
import time
import pyaudio

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
    "ESP32/MinhaCasa/QuartoRobson/Temperatura": "temperatura"
}

# falar
texto_fala = pyttsx3.init()
paused = False

def falar(audio):
    rate = texto_fala.getProperty('rate')
    texto_fala.setProperty('rate', 160)
    voices = texto_fala.getProperty('voices')
    texto_fala.setProperty('voice', voices[3].id)# Trocar as vozes
    texto_fala.say(audio)
    texto_fala.runAndWait()
    time.sleep(0.7)  # Adiciona uma pausa de 1 segundo após cada fala

def hora():
    Hora: str = datetime.datetime.now().strftime("%#H horas e,:%#M minutos,")
    falar("Agora são,")
    falar(Hora)

def obter_nome_mes(numero_mes):
    meses = {
        1: "Janeiro!",
        2: "Fevereiro!",
        3: "Março!",
        4: "Abril!",
        5: "Maio!",
        6: "Junho!",
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

    falar("A data de hoje é....," + dia)
    falar("de-----,   " + mes)
    falar("de----- ,  " + ano)

def bem_vindo():
    falar("Olá Robson Brasil, bem-vindo de volta!")
    hora()
    data()

    periodo_do_dia = datetime.datetime.now().hour
    if periodo_do_dia >= 6 and periodo_do_dia < 12:
        falar("Bom dia mestre,")
    elif periodo_do_dia >= 12 and periodo_do_dia < 18:
        falar("Boa tarde mestre,")
    elif periodo_do_dia >= 18 and periodo_do_dia <= 24:
        falar("Boa noite mestre,")
        falar("Jarvis a sua disposição! Diga-me como posso ajudá-lo hoje?,")
    else:
        falar("Mestre, vá dormir, já é de madrugada!,")

assistant_active = True

def on_message(client, userdata, message):
    global assistant_active
    payload = message.payload.decode("utf-8")

def microfone():
    r = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            r.pause_threshold = 1
            r.adjust_for_ambient_noise(source, duration=1.0)
            audio = r.listen(source)
            print("Reconhecendo o Comando")
            comando = r.recognize_google(audio, language='pt-BR')
            comando = comando.lower()
            print(comando)
            if 'jarvis' in comando:
                comando = comando.replace('jarvis', '')
                #texto_fala.say(comandoo)
                texto_fala.runAndWait()

    except Exception as e:
        print(e)
        #falar(" Por favor, repita. Não entendi.")
        return None

    return comando

# Configurar o cliente MQTT
client = mqtt.Client()
client.username_pw_set(mqtt_user, mqtt_password)
client.connect(mqtt_server, mqtt_port, 60)

if __name__ == "__main__":
    bem_vindo()

    while True:
        print("Estou Escutando....")
        if assistant_active:
            comando = microfone()
        if comando is not None:
            comando = comando.lower()
        if comando is not None and 'como você está' in comando:
            falar("Estou bem, obrigado. E você?")
            falar("O que posso fazer para ajudá-lo, mestre?")
        elif comando is not None and 'hora' in comando:
            hora()
        elif comando is not None and 'data' in comando:
            data()

        for topic in relay_topics:
            alias = topic_aliases[topic]
            if comando is not None and f"acender {alias}" in comando:
                client.publish(topic, "1")
                falar(f"Ligando o {alias}")
            elif comando is not None and f"apagar {alias}" in comando:
                client.publish(topic, "0")
                falar(f"Apagando o {alias}")
            elif comando is not None and f"temperatura {alias}" in comando:
                client.publish(topic, "get_temp_data")  # Publicar mensagem para obter dados de temperatura
                client.publish(topic, "get_hum_data")  # Publicar mensagem para obter dados de umidade
                # Aguardar a chegada dos dados do sensor
                # Substitua as linhas abaixo pela lógica necessária para receber os dados do sensor
                str_temp_data = "<dados_de_temperatura>"  # Substitua com os dados reais
                str_hum_data = "<dados_de_umidade>"  # Substitua com os dados reais
                if str_temp_data is not None:
                    falar("Aguarde um momento enquanto eu verifico a temperatura para você: " + str_temp_data)
                else:
                    falar("Desculpe, não foi possível obter os dados de temperatura no momento.")
