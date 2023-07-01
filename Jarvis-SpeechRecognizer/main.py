import datetime
import os
import sys
import threading
import time
import keyboard
import paho.mqtt.client as mqtt
import pygame
import cv2
import moviepy.editor as mp
from moviepy.editor import VideoFileClip
import pyttsx3
import pywhatkit
import requests
import speech_recognition as sr
import wikipedia
from num2words import num2words

from ConfiguracaoMQTT import mqtt_server, mqtt_port, mqtt_user, mqtt_password
from topicos_mqtt import relay_topics
from topicos_mqtt_aliases import topic_aliases

def on_message(client, userdata, message):
    payload = message.payload.decode("utf-8")
    print("Received message: ", payload)

# Configuração do cliente MQTT
client = mqtt.Client()
client.username_pw_set(mqtt_user, mqtt_password)
client.connect(mqtt_server, mqtt_port, 60)
client.loop_start()

sys.stdout.reconfigure(encoding='utf-8')

# falar
maquina_fala = pyttsx3.init("sapi5")

# Variável para controlar se o programa principal está em pausa ou não
pause = False

def microfone():
    #maquina_fala = pyttsx3.init()

    comando = None  # Added the initialization of 'comando'

    r = sr.Recognizer()

    try:
        print("Estou Escutando....")

        with sr.Microphone(sample_rate=16000) as source:
            r.pause_threshold = 0.5
            r.adjust_for_ambient_noise(source, duration=0.15)
            audio = r.listen(source)
            comando = r.recognize_google(audio, language='pt-BR')
            comando = comando.lower()
            comando = comando.replace('jarvis', 'Jarvis').replace('jarvis', '')
            
            print(comando)
            print("Reconhecendo o Comando")

    except Exception as e:
        print(e)
        return None

    return comando

def player_video(caminho_video, caminho_musica):
    # Carregar o vídeo usando o moviepy
    video = mp.VideoFileClip(caminho_video)

    # Extrair o áudio do arquivo de vídeo
    audio_video = video.audio

    # Configurações do pygame para reprodução de áudio
    pygame.mixer.init()
    pygame.mixer.music.load(caminho_musica)
    pygame.mixer.music.play()

    # Definir o tempo inicial
    tempo_inicial = time.time()

    # Duração do vídeo igual à duração da música
    duracao = pygame.mixer.Sound(caminho_musica).get_length()

    # Desativar o reconhecimento de voz durante a reprodução do vídeo
    recognizer = sr.Recognizer()
    recognizer.pause_threshold = float('inf')  # Definir pausa infinita para desativar o reconhecimento
    recognizer.energy_threshold = 4000  # Ajuste o valor conforme necessário para evitar o reconhecimento de ruído

    # Loop para reproduzir o vídeo em loop pela duração da música
    while time.time() - tempo_inicial < duracao:
        # Obter o quadro correspondente ao tempo atual
        frame = video.get_frame(time.time() - tempo_inicial)

        # Converter o quadro para o formato BGR (OpenCV usa BGR)
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # Exibir o quadro usando o OpenCV
        cv2.imshow("Video Player", frame_bgr)

        # Verificar se a tecla 'q' foi pressionada para sair
        if cv2.waitKey(1) == ord('q'):
            break

    # Reativar o reconhecimento de voz após a reprodução do vídeo
    recognizer.pause_threshold = 90.0  # Definir o valor desejado para retomar o reconhecimento
    recognizer.energy_threshold = 1000  # Ajuste o valor conforme necessário para detectar a fala

    # Parar a reprodução do áudio do vídeo e do pygame
    pygame.mixer.music.stop()
    audio_video.close()

    # Liberar recursos
    cv2.destroyAllWindows()

# Iniciar a reprodução da música ao iniciar o assistente
caminho_musica = "D:\GitRepositorio\Projetos-em-Python\Jarvis-SpeechRecognizer\IntroduçãoJARVIS.mp3"  # Substitua pelo caminho correto do arquivo de música

# Desativar o reconhecimento de voz antes de iniciar a reprodução do vídeo
recognizer = sr.Recognizer()
recognizer.pause_threshold = float('inf')  # Definir pausa infinita para desativar o reconhecimento
recognizer.energy_threshold = 10000  # Ajuste o valor conforme necessário para evitar o reconhecimento de ruído

# Iniciar a reprodução do vídeo
caminho_video = "D:\GitRepositorio\Projetos-em-Python\Jarvis-SpeechRecognizer\J.A.R.V.I.S.mp4"  # Substitua pelo caminho correto do arquivo de vídeo
player_video(caminho_video, caminho_musica)

#Reativar o reconhecimento de voz após a reprodução do vídeo
recognizer.pause_threshold = 90.0  # Definir o valor desejado para retomar o reconhecimento
recognizer.energy_threshold = 5000  # Ajuste o valor conforme necessário para detectar a fala

#Aguardar o término da reprodução da música antes de continuar com as saudações
while pygame.mixer.music.get_busy():
    continue

#Ativar o reconhecimento de voz novamente
recognizer.pause_threshold = 90.0  # Definir o valor desejado para o reconhecimento
recognizer.energy_threshold = 5000  # Ajuste o valor conforme necessário para detectar a fala

# Configuraçoes da voz, timbre, voz, e pausa de fala
def falar(audio):
    maquina_fala.say(audio)
    maquina_fala.runAndWait()
    rate = maquina_fala.getProperty('rate')
    maquina_fala.setProperty('rate', 115)  # Trocar a velocidade da voz
    voices = maquina_fala.getProperty('voices')
    maquina_fala.setProperty('voice', voices[3].id)  # Trocar as vozes
    time.sleep(0.5)  # Adiciona uma pausa de 1 segundo após cada fala

# Configuração da hora na qual o assistente fala
def hora():
    Hora: str = datetime.datetime.now().strftime("%#H horas e:%#M minutos  .....!")
    falar("Agora são....:  ")
    falar(Hora)
    maquina_fala.runAndWait()

# Configuração adicional para o assistente falar o nome do mês vindouro e não o numeral!
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

# Configuração da Data e Mês
def data():
    now = datetime.datetime.now()
    dia = str(now.day)
    mes = obter_nome_mes(now.month)
    ano = str(now.year)

    # Convert year to words
    year_in_words = num2words(ano, lang='pt_BR')

    falar("A data de hoje é:" + dia)
    
    falar("de:" + mes)
    
    falar("de:" + year_in_words)
    maquina_fala.runAndWait()

# Saudação inicial, isso será dito na inicialização do assistente
def bem_vindo():
    falar("Olá Robson Brasil, bem-vindo de volta,.  !")
    maquina_fala.runAndWait()
    hora()
    data()

    periodo_do_dia = datetime.datetime.now().hour
    if periodo_do_dia >= 6 and periodo_do_dia < 12:
        falar("Bom dia mestre!")
        maquina_fala.runAndWait()
    elif periodo_do_dia >= 12 and periodo_do_dia < 18:
        falar("Boa tarde mestre!")
        maquina_fala.runAndWait()
    elif periodo_do_dia >= 18 and periodo_do_dia <= 24:
        falar("Boa noite mestre!")
        maquina_fala.runAndWait()
        falar("Jarvis a sua disposição, Diga-me, como posso ajudá-lo?")
        maquina_fala.runAndWait()
    else:
        falar("Mestre, vá dormir, já é de madrugada!")
        maquina_fala.runAndWait()

assistant_active = True

# Início da configuração da pausa
def definir_tempo_pausa():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        falar("Diga o tempo de pausa desejado:")
        maquina_fala.runAndWait()
        audio = recognizer.listen(source)

    try:
        texto = recognizer.recognize_google(audio, language="pt-BR")
        tempo_pausa = extrair_valor_tempo(
            texto)  # Implemente a função extrair_valor_tempo() para converter a entrada em um valor numérico de tempo.
        falar(f"Tempo de pausa definido como {tempo_pausa} segundos.")
        maquina_fala.runAndWait()
        return tempo_pausa
    except sr.UnknownValueError:
        print("Não foi possível entender a entrada de voz.")
    except sr.RequestError:
        print("Não foi possível se conectar ao serviço de reconhecimento de voz.")
    return None

# Definição por voz, de quantos segundos, minutos e/ou horas o assistente deverá ficar pausado
def extrair_valor_tempo(texto):
    palavras = texto.split()  # Divide o texto em palavras

    # Procura pela palavra "segundos" ou "minutos"
    if "segundos" in palavras:
        indice = palavras.index("segundos")
        if indice > 0:
            try:
                tempo = int(palavras[indice - 1])  # Obtém o valor numérico antes da palavra "segundos"
                return tempo
            except ValueError:
                pass

    if "minutos" in palavras:
        indice = palavras.index("minutos")
        if indice > 0:
            try:
                tempo = int(palavras[
                                indice - 1]) * 60  # Obtém o valor numérico antes da palavra "minutos" e converte para segundos
                return tempo
            except ValueError:
                pass

    if "hora" in palavras or "horas" in palavras:
        if "hora" in palavras:
            indice = palavras.index("hora")
        else:
            indice = palavras.index("horas")
        if indice > 0:
            try:
                tempo = int(palavras[
                                indice - 1]) * 3600  # Obtém o valor numérico antes da palavra "horas" e converte para segundos
                return tempo
            except ValueError:
                pass

    return None  # Retorna None se o formato do tempo não for reconhecido

def fala(mensagem):
    maquina_fala.say(mensagem)

def stop_assistant(falar_mensagem=True):
    assistant_active = [True]  # Inicialmente, o assistente está ativo
    if falar_mensagem:
        falar("Assistente entrando em pausa....")
        maquina_fala.runAndWait()

    tempo_pausa = definir_tempo_pausa()
    if tempo_pausa is None:
        tempo_pausa = 10  # Tempo de pausa padrão em segundos

    def retomar_execucao(assistant_active):
        assistant_active[0] = True

    # Monitorar a tecla "A" e a palavra "ativar" para interromper a pausa e reativar o assistente
    def on_key_press(key):
        if key.name == "ctrl+alt+m":
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
        maquina_fala.runAndWait()

# Esse comando era pra ser acionado mesmo quando o assistente estivesse em pausa, mas, não consegui fazer funcionar, ainda!
def activate_assistant():
    global assistant_active
    assistant_active = True
    falar("Assistente ativado.")
    maquina_fala.runAndWait()

# Comando para desligar o assistente
def shutdown_assistant():
    falar("Desligando o assistente.")
    maquina_fala.runAndWait()
    sys.exit()

# Comando para a previsão do Tempo, aqui será obrigatório o uso de uma API
def obter_previsao_tempo(localizacao, chave_api):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={localizacao}&appid={chave_api}&units=metric"
    response = requests.get(url)
    dados = response.json()

    # Dicionário de tradução das descrições do tempo
    traducoes = {
        "clear sky": "Limpo",
        "few clouds": "com Poucas Nuvens",
        "scattered clouds": "com Nuvens Dispersas",
        "broken clouds": "com Nuvens Quebradas",
        "shower rain": "com Chuva Fraca",
        "rain": "com Chuva",
        "thunderstorm": "com Trovoada",
        "snow": "Neve",
        "mist": "com Névoa",
        "overcast clouds": "com nuvens encobertas",
    }

    # Verifique se a requisição foi bem-sucedida
    if response.status_code == 200:
        # Extraia as informações relevantes da resposta JSON
        temperatura = dados["main"]["temp"]
        descricao = dados["weather"][0]["description"]
        descricao_traduzida = traducoes.get(descricao,
                                            descricao)  # Utiliza o dicionário de traduções ou mantém a descrição original
        umidade = dados["main"]["humidity"]

        return f"A TEMPERATURA em {localizacao} é de {temperatura}° Celsius, céu {descricao_traduzida}. A UMIDADE do Ar é de {umidade}%."
    else:
        return "Não foi possível obter a previsão do tempo."

# Configuração da previsão do tempo
localizacao = "Manaus, Amazonas"  # Substitua pela localização desejada
# ToDo: Por aqui a tua API
chave_api = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"  # Substitua pela sua chave de API da OpenWeatherMap

# O assistente falar a previsão em si!
previsao = obter_previsao_tempo(localizacao, chave_api)
print(previsao)
falar(previsao)
maquina_fala.runAndWait()

if __name__ == "__main__":
    bem_vindo()
    obter_previsao_tempo(localizacao, chave_api)
    maquina_fala.runAndWait()

    try:
        while True:

            comando = microfone()

            if assistant_active and comando is not None:
                comando = comando.lower()

            print("Estou Escutando....")

            if comando is not None and 'como você está' in comando:
                falar("Estou bem, obrigado. E você?")
                falar("O que posso fazer para ajudá-lo, mestre?")

            elif comando is not None and 'hora' in comando:
                hora()
            elif comando is not None and 'data' in comando:
                data()

            elif comando is not None and 'fazer uma pausa' in comando:
                stop_assistant()
            elif comando is not None and 'ativar' in comando:
                activate_assistant()
            elif comando is not None and 'desligar' in comando:
                desligar = comando.replace('desligar', '')
                shutdown_assistant()

            elif comando is not None and 'procurar' in comando:
                procurar = comando.replace('procurar', '')
                wikipedia.set_lang('pt')
                resultado = wikipedia.summary(procurar, 2)
                print(resultado)
                falar(resultado)
                maquina_fala.runAndWait()

            elif comando is not None and 'tocar' in comando:
                musica = comando.replace('tocar', '')
                resultado = pywhatkit.playonyt(musica)
                falar('Tocando música')
                maquina_fala.runAndWait()

            elif comando is not None and "player de música".lower() in comando.lower():
                winamp_path = r"C:/Program Files (x86)/Winamp/winamp.exe"
                os.startfile(winamp_path)

            elif comando is not None and 'previsão do tempo' in comando:
                previsao = obter_previsao_tempo(localizacao, chave_api)
                print(previsao)
                falar("Hoje...")
                maquina_fala.runAndWait()
                falar(previsao)
                maquina_fala.runAndWait()

            for topic in relay_topics:
                alias = topic_aliases[topic]

                if comando is not None and f"acender {alias.lower()}" in comando:
                    client.publish(topic, "1")
                    falar(f"Ligando o {alias}")

                elif comando is not None and f"apagar {alias.lower()}" in comando:
                    client.publish(topic, "0")
                    falar(f"Apagando o {alias}")

    except KeyboardInterrupt:
        pass
