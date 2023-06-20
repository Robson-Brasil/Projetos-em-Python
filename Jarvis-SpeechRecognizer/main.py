import speech_recognition as sr
import pyttsx3
import paho.mqtt.client as mqtt
import sys
import datetime
import time
import pyaudio
import threading
import keyboard
import wikipedia
import pywhatkit
import requests
import json
from gtts import gTTS
import os
import credenciais

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

# Variável para controlar se o programa principal está em pausa ou não
pause = False

def falar(audio):
    rate = texto_fala.getProperty('rate')
    texto_fala.setProperty('rate', 160)
    voices = texto_fala.getProperty('voices')
    texto_fala.setProperty('voice', voices[3].id)# Trocar as vozes
    texto_fala.say(audio)
    texto_fala.runAndWait()
    time.sleep(0.1)  # Adiciona uma pausa de 1 segundo após cada fala

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

def on_message(message):
    global assistant_active
    payload = message.payload.decode("utf-8")

def microfone():

    comando = None  # Added the initialization of 'comando'

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

def stop_assistant(falar_mensagem=True):
    assistant_active = [True]  # Inicialmente, o assistente está ativo
    if falar_mensagem:
        falar("Assistente pausado.")

    tempo_pausa = 10  # Tempo de pausa em segundos

    def retomar_execucao(assistant_active):
        assistant_active[0] = True

    # Monitorar a tecla "A" e a palavra "ativar" para interromper a pausa e reativar o assistente
    def on_key_press(key):
        if key.name == "a":
            retomar_execucao(assistant_active)
        else:
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                print("Diga algo...")
                audio = recognizer.listen(source)

            try:
                comando = recognizer.recognize_google(audio, language="pt-BR")
                print("Comando reconhecido:", comando)
                comando = comando.lower()

                if "ativar" in comando:
                    retomar_execucao(assistant_active)
            except sr.UnknownValueError:
                print("Não foi possível reconhecer o comando.")

    keyboard.on_press(on_key_press)

    # Agendar a função de retomada após o tempo de pausa
    thread_retomada = threading.Timer(tempo_pausa, retomar_execucao, args=(assistant_active,))
    thread_retomada.start()

    # Esperar até que a thread de retomada termine ou a tecla seja pressionada
    thread_retomada.join()

    if falar_mensagem:
        falar("Assistente reativado.")
    texto_fala.runAndWait()
def activate_assistant():
    global assistant_active
    assistant_active = True
    falar("Assistente ativado.")

def shutdown_assistant():
    falar("Desligando o assistente.")
    sys.exit()

def obter_previsao_tempo(localizacao, chave_api):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={localizacao}&appid={credenciais.chave_api}&units=metric"
    response = requests.get(url)
    dados = response.json()

    # Dicionário de tradução das descrições do tempo
    traducoes = {
        "clear sky": "céu limpo",
        "few clouds": "poucas nuvens",
        "scattered clouds": "nuvens dispersas",
        "broken clouds": "nuvens quebradas",
        "shower rain": "chuva fraca",
        "rain": "chuva",
        "thunderstorm": "trovoada",
        "snow": "neve",
        "mist": "névoa",
    }

    # Verifique se a requisição foi bem-sucedida
    if response.status_code == 200:
        # Extraia as informações relevantes da resposta JSON
        temperatura = dados["main"]["temp"]
        descricao = dados["weather"][0]["description"]
        descricao_traduzida = traducoes.get(descricao, descricao)  # Utiliza o dicionário de traduções ou mantém a descrição original
        umidade = dados["main"]["humidity"]

        return f"A temperatura em {localizacao} é de {temperatura}°C. {descricao_traduzida}. A umidade é de {umidade}%."
    else:
        return "Não foi possível obter a previsão do tempo."

localizacao = "Manaus,BR"  # Substitua pela localização desejada


previsao = obter_previsao_tempo(localizacao, chave_api)
print(previsao)
falar(previsao)

if __name__ == "__main__":
    bem_vindo()
    obter_previsao_tempo(localizacao, chave_api)

    try:
        while True:
            print("Estou Escutando....")
            if assistant_active:
                comando = microfone()
            if comando is not None:
                comando = comando.lower()

            if comando is not None and 'como você está' in comando:
                falar("Estou bem, obrigado. E você?")
                falar("O que posso fazer para ajudá-lo, mestre?")
                texto_fala.runAndWait()
            elif comando is not None and 'hora' in comando:
                hora()
                texto_fala.runAndWait()
            elif comando is not None and 'data' in comando:
                data()
                texto_fala.runAndWait()

            elif comando is not None and 'fazer uma pausa' in comando:
                stop_assistant()
                texto_fala.runAndWait()
            elif comando is not None and 'ativar' in comando:
                activate_assistant()
                texto_fala.runAndWait()
            elif comando is not None and 'desligar' in comando:
                shutdown_assistant()
                texto_fala.runAndWait()

            elif comando is not None and 'procurar por' in comando:
                procurar = comando.replace('procurar por', '')
                wikipedia.set_lang('pt')
                resultado = wikipedia.summary(procurar, 2)
                print(resultado)
                falar(resultado)
                texto_fala.runAndWait()

            elif comando is not None and 'toque' in comando:
                musica = comando.replace('toque', '')
                resultado = pywhatkit.playonyt(musica)
                falar('Tocando música')
                texto_fala.runAndWait()

            elif comando is not None and 'previsão do tempo' in comando:
                previsao = obter_previsao_tempo(localizacao, chave_api)
                print(previsao)
                falar(previsao)

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

    except KeyboardInterrupt:
        pass