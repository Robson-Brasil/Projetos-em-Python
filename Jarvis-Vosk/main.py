import pyttsx3
import paho.mqtt.client as mqtt
import sys
import datetime
import time
import requests
import json
from vosk import Model, KaldiRecognizer
import pyaudio
import keyboard
import pygame
import pywhatkit
import wikipedia
import sounddevice as sd
import numpy as np


# Inicializar o TTS
engine = pyttsx3.init()

sys.stdout.reconfigure(encoding='utf-8')

def tocar_musica(caminho):
    pygame.mixer.init()
    pygame.mixer.music.load(caminho)
    pygame.mixer.music.play()


# Iniciar a reprodução da música ao iniciar o assistente
caminho_musica = "D:\GitRepositorio\Projetos-em-Python\Jarvis-SpeechRecognizer\IntroduçãoJARVIS.mp3"  # Substitua pelo caminho correto do arquivo de música
tocar_musica(caminho_musica)

# Aguardar um tempo para a música tocar antes de continuar com as saudações
tempo_espera = 23  # Tempo em segundos, ajuste conforme necessário
time.sleep(tempo_espera)

def falar(texto):
    engine.say(texto)
    rate = engine.getProperty('rate')
    engine.setProperty('rate', 180)
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[3].id)  # Trocar as vozes
    engine.runAndWait()
    time.sleep(0.8)  # Adiciona uma pausa de 0,5 segundos após cada fala

def on_message(client, userdata, message):
    global assistant_active
    payload = message.payload.decode("utf-8")

    while True:
        print("Estou Escutando....")
        if assistant_active:
            comando = microfone().lower()# Aguardar um tempo para a música tocar antes de continuar com as saudações
            tempo_espera = 3  # Tempo em segundos, ajuste conforme necessário
            time.sleep(tempo_espera)


        # Rest of the code...

        client.loop()

def calibrar_microfone():
    print("Realizando a calibração do microfone. Aguarde...")
    duration = 3  # Duração da gravação para calibração (em segundos)
    fs = 44100  # Taxa de amostragem do áudio
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()  # Aguarda a gravação ser concluída
    print("Calibração concluída.")

    return audio


def microfone():

    model = Model(r"D:\\GitRepositorio\\Projetos-em-Python\\Jarvis-Vosk\\model")
    rec = KaldiRecognizer(model, 44100)

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
    stream.start_stream()

    texto = ""

    while True:
        data = stream.read(8192)  # Ler uma pequena quantidade de áudio do fluxo

        if rec.AcceptWaveform(data):
            result = rec.Result()
            result_json = json.loads(result)
            comando = result_json['text']
            print(comando)
            break

    stream.stop_stream()
    stream.close()
    p.terminate()

    return comando.lower().strip()

def hora():
    Hora = datetime.datetime.now().strftime("%#H horas e:%#M minutos")
    falar("Agora são")
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
    hora()
    data()
    falar("Olá Robson Brasil, seja bem vindo de volta,")

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


# Configuração do MQTT
mqtt_username = "RobsonBrasil"
mqtt_password = "loboalfa"
mqtt_broker = "192.168.15.10"
mqtt_port = 1883

client = mqtt.Client()
client.username_pw_set(mqtt_username, mqtt_password)
client.connect(mqtt_broker, mqtt_port)

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

def obter_previsao_tempo(localizacao, chave_api):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={localizacao}&appid={chave_api}&units=metric"
    response = requests.get(url)
    dados = response.json()

    # Dicionário de tradução das descrições do tempo
    traducoes = {
        "clear sky": "Céu Limpo",
        "few clouds": "Poucas Nuvens",
        "scattered clouds": "Nuvens Dispersas",
        "broken clouds": "Nuvens Quebradas",
        "shower rain": "Chuva Fraca",
        "rain": "Chuva",
        "thunderstorm": "Trovoada",
        "snow": "Neve",
        "mist": "Névoa",
        "light rain": "Chuva Fraca",
    }

    # Verifique se a requisição foi bem-sucedida
    if response.status_code == 200:
        # Extraia as informações relevantes da resposta JSON
        temperatura = dados["main"]["temp"]
        descricao = dados["weather"][0]["description"]
        descricao_traduzida = traducoes.get(descricao,
                                            descricao)  # Utiliza o dicionário de traduções ou mantém a descrição original
        umidade = dados["main"]["humidity"]

        return f"A TEMPERATURA em {localizacao} é de {temperatura}°C. {descricao_traduzida}. A UMIDADE do Ar é de {umidade}%."
    else:
        return "Não foi possível obter a previsão do tempo."


# Configuração da previsão do tempo
localizacao = "Manaus, Amazonas"  # Substitua pela localização desejada
# ToDo: Por aqui a tua API
chave_api = "b7d14b931a96d7a64ea1aba822899328"  # Substitua pela sua chave de API da OpenWeatherMap

# O assistente falar a previsão em si!
previsao = obter_previsao_tempo(localizacao, chave_api)
print(previsao)
falar(previsao)
engine.runAndWait()

if __name__ == "__main__":
    bem_vindo()

    while True:
        model = Model(r"D:\\GitRepositorio\\Projetos-em-Python\\Jarvis-Vosk\\model")
        rec = KaldiRecognizer(model, 44100)
        print("Estou Escutando....")
        comando = microfone().lower()

        if 'como você está' in comando:
            falar("Estou bem, obrigado e você,")
            falar("o que posso fazer para ajudá-lo mestre,")

        elif 'hora' in comando:
            hora()
            engine.runAndWait()

        elif 'data' in comando:
            data()
            engine.runAndWait()

        elif 'fazer uma pausa' in comando:
            stop_assistant()
            engine.runAndWait()

        elif 'ativar' in comando:
            activate_assistant()
            engine.runAndWait()

        elif 'desligar' in comando:
            desligar = comando.replace('desligar', '')
            shutdown_assistant()
            engine.runAndWait()

        elif 'procurar' in comando:
            procurar = comando.replace('procurar', '')
            wikipedia.set_lang('pt')
            resultado = wikipedia.summary(procurar, 2)
            print(resultado)
            falar(resultado)
            engine.runAndWait()

        elif 'tocar' in comando:
            musica = comando.replace('tocar', '')
            resultado = pywhatkit.playonyt(musica)
            falar('Tocando música')
            engine.runAndWait()

        elif 'player de música'.lower() in comando.lower():
            winamp_path = r"C:/Program Files (x86)/Winamp/winamp.exe"
            os.startfile(winamp_path)

        elif 'previsão do tempo' in comando:
            previsao = obter_previsao_tempo(localizacao, chave_api)
            print(previsao)
            falar("Hoje...")
            falar(previsao)

        for topic in relay_topics:
            alias = topic_aliases[topic]
            if f"acender {alias}" in comando:
                client.publish(topic, "1")
                falar(f"Ligando o, {alias}")

            elif f"apagar {alias}" in comando:
                client.publish(topic, "0")
                falar(f"Apagando o, {alias}")