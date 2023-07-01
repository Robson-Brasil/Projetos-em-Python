import datetime
from email import message
import webbrowser
from numpy import tile
import pyttsx3
import speech_recognition
import requests
from bs4 import BeautifulSoup
import os
import pyautogui
import random
from plyer import notification
from pygame import mixer
import speedtest
import paho.mqtt.client as mqtt
import sys

from ConfiguracaoMQTT import mqtt_server, mqtt_port, mqtt_user, mqtt_password
from topicos_mqtt import relay_topics
from topicos_mqtt_aliases import topic_aliases

sys.stdout.reconfigure(encoding='utf-8')

# Função para publicar uma mensagem MQTT
def publish_mqtt(topic, message):
    client = mqtt.Client()
    client.username_pw_set(mqtt_user, mqtt_password)
    client.connect(mqtt_server, mqtt_port)
    client.publish(topic, message)
    client.disconnect()

# Função de callback para conexão MQTT
def on_connect(client, userdata, flags, rc):
    print("Conectado ao broker MQTT.")
    client.subscribe("ESP32/MinhaCasa/QuartoRobson/Interruptor1/Comando")
    client.subscribe("ESP32/MinhaCasa/QuartoRobson/Interruptor2/Comando")
    client.subscribe("ESP32/MinhaCasa/QuartoRobson/Interruptor3/Comando")
    client.subscribe("ESP32/MinhaCasa/QuartoRobson/Interruptor4/Comando")
    client.subscribe("ESP32/MinhaCasa/QuartoRobson/Interruptor5/Comando")
    client.subscribe("ESP32/MinhaCasa/QuartoRobson/Interruptor6/Comando")
    client.subscribe("ESP32/MinhaCasa/QuartoRobson/Interruptor7/Comando")
    client.subscribe("ESP32/MinhaCasa/QuartoRobson/Interruptor8/Comando")

# Função de callback para recebimento de mensagens MQTT
def on_message(client, userdata, msg):
    print("Mensagem recebida no tópico: " + msg.topic)
    print("Conteúdo da mensagem: " + msg.payload.decode())

# Configuração do cliente MQTT
client = mqtt.Client()
client.username_pw_set(mqtt_user, mqtt_password)
client.on_connect = on_connect
client.on_message = on_message
client.connect(mqtt_server, mqtt_port, keepalive=60)
client.loop_start()

for i in range(3):
    a = input("Senhor, digite a senha de segurança, por favor :- ")
    pw_file = open("password.txt","r")
    pw = pw_file.read()
    pw_file.close()
    if (a==pw):
        print("Bem-Vindo Senhor! Por Favor fale [JARVIS ATIVAR] Para eu carregar o sistema!")
        break
    elif (i==2 and a!=pw):
        exit()

    elif (a!=pw):
        print("Tente Novamente")

from INTRO import play_gif
play_gif

engine = pyttsx3.init("sapi5")
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[3].id)
rate = engine.setProperty("rate",170)

def speak(audio):
    engine.say(audio)
    engine.runAndWait()

def takeCommand():
    r = speech_recognition.Recognizer()
    with speech_recognition.Microphone() as source:
        print("Ouvindo.....")
        r.pause_threshold = 1
        r.energy_threshold = 300
        audio = r.listen(source,0,4)

    try:
        print("Entendendo..")
        query  = r.recognize_google(audio,language='pt-BR')
        print(f"Você disse: {query}\n")
    except Exception as e:
        print("Diga isso novamente")
        return "None"
    return query

def alarm(query):
    timehere = open("Alarmtext.txt","a")
    timehere.write(query)
    timehere.close()
    os.startfile("alarm.py")

if __name__ == "__main__":
    while True:
        query = takeCommand().lower()
        if "ativar" in query:
            from GreetMe import greetMe
            greetMe()

            while True:
                query = takeCommand().lower()
                if "vá dormir" in query:
                    speak("Certo, senhor. Você pode me ligar a qualquer momento")
                    break

                elif "alterar senha" in query:
                    speak("Qual é a nova senha")
                    new_pw = input("Digite a nova senha\n")
                    new_password = open("password.txt","w")
                    new_password.write(new_pw)
                    new_password.close()
                    speak("Feito, senhor")
                    speak(f"Sua nova senha é{new_pw}")

                elif "agende meu dia" in query:
                    tasks = [] #Empty list 
                    speak("Você deseja limpar as tarefas antigas? (Por favor, responda SIM ou NÃO)")
                    query = takeCommand().lower()
                    if "sim" in query:
                        file = open("tasks.txt","w")
                        file.write(f"")
                        file.close()
                        no_tasks = int(input("Digite o número de tarefas:- "))
                        i = 0
                        for i in range(no_tasks):
                            tasks.append(input("Digite a tarefa:- "))
                            file = open("tasks.txt","a")
                            file.write(f"{i}. {tasks[i]}\n")
                            file.close()
                    elif "não" in query:
                        i = 0
                        no_tasks = int(input("Digite o número de tarefas:- "))
                        for i in range(no_tasks):
                            tasks.append(input("Digite a tarefa:- "))
                            file = open("tasks.txt","a")
                            file.write(f"{i}. {tasks[i]}\n")
                            file.close()

                elif "mostrar minha agenda" in query:
                    file = open("tasks.txt","r")
                    content = file.read()
                    file.close()
                    mixer.init()
                    mixer.music.load("notification.mp3")
                    mixer.music.play()
                    notification.notify(
                        title = "Minha agenda :-",
                        message = content,
                        timeout = 15
                    )

                elif "modo de foco" in query:
                    a = int(input("Você tem certeza de que deseja entrar no modo de foco :- [1 para SIM / 2 para NÃO "))
                    if (a==1):
                        speak("Entrando no modo de foco....")
                        os.startfile("D:\\Coding\\Youtube\\Jarvis\\FocusMode.py")
                        exit()

                    else:
                        pass

                elif "Mostrar meu foco" in query:
                    from FocusGraph import focus_graph
                    focus_graph()

                elif "tradutor" in query:
                    from Translator import translategl
                    query = query.replace("jarvis","")
                    query = query.replace("tradutor","")
                    translategl(query)

                elif "open" in query:   #EASY METHOD
                    query = query.replace("open","")
                    query = query.replace("jarvis","")
                    pyautogui.press("super")
                    pyautogui.typewrite(query)
                    pyautogui.sleep(2)
                    pyautogui.press("enter")                       

                elif "velocidade da internet" in query:
                    cabo = speedtest.Speedtest()
                    cabo.get_best_server()
                    upload_net = cabo.upload() / 1048576  # Megabyte = 1024*1024 Bytes
                    download_net = cabo.download() / 1048576
                    print("Cable Upload Speed is", upload_net)
                    print("Cable download speed is ", download_net)
                    speak(f"Cable download speed is {download_net}")
                    speak(f"Cable Upload speed is {upload_net}")

                elif "ipl score" in query:
                    from plyer import notification  #pip install plyer
                    import requests #pip install requests
                    from bs4 import BeautifulSoup #pip install bs4
                    url = "https://www.cricbuzz.com/"
                    page = requests.get(url)
                    soup = BeautifulSoup(page.text,"html.parser")
                    team1 = soup.find_all(class_ = "cb-ovr-flo cb-hmscg-tm-nm")[0].get_text()
                    team2 = soup.find_all(class_ = "cb-ovr-flo cb-hmscg-tm-nm")[1].get_text()
                    team1_score = soup.find_all(class_ = "cb-ovr-flo")[8].get_text()
                    team2_score = soup.find_all(class_ = "cb-ovr-flo")[10].get_text()

                    a = print(f"{team1} : {team1_score}")
                    b = print(f"{team2} : {team2_score}")

                    notification.notify(
                        title = "IPL SCORE :- ",
                        message = f"{team1} : {team1_score}\n {team2} : {team2_score}",
                        timeout = 15
                    )

                elif "play um jogo" in query:
                    from game import game_play
                    game_play()

                elif "screenshot" in query:
                    import pyautogui #pip install pyautogui
                    im = pyautogui.screenshot()
                    im.save("ss.jpg")

                elif "tire uma foto minha" in query:
                    pyautogui.press("super")
                    pyautogui.typewrite("camera")
                    pyautogui.press("enter")
                    pyautogui.sleep(2)
                    speak("SMILE")
                    pyautogui.press("enter")

                elif "jarvis, como você está?" in query:
                    speak("Estou bem, obrigado e você ?")
                elif "estou ótimo" in query:
                    speak("Isso é ótimo, senhor")
                elif "como você está" in query:
                    speak("Perfeito, senhor")
                elif "obrigado" in query:
                    speak("seja-benvindo, senhor")

                elif "cansado" in query:
                    speak("Reproduzindo suas músicas favoritas, senhor")
                    a = (1,2,3)
                    b = random.choice(a)
                    if b==1:
                        webbrowser.open("https://www.youtube.com/watch?v=xF3x3jTvTYg")

                elif "pausa" in query:
                    pyautogui.press("k")
                    speak("video paused")
                elif "play" in query:
                    pyautogui.press("k")
                    speak("video played")
                elif "mudo" in query:
                    pyautogui.press("m")
                    speak("video mutado")

                elif "aumentar volume" in query:
                    from keyboard import volumeup
                    speak("Aumentando o volume, senhor")
                    volumeup()
                elif "abaixar volume" in query:
                    from keyboard import volumedown
                    speak("Abaixando o volume, senhor")
                    volumedown()

                elif "abrir o" in query:
                    from Dictapp import openappweb
                    openappweb(query)
                elif "fechar o" in query:
                    from Dictapp import closeappweb
                    closeappweb(query)

                elif "google" in query:
                    from SearchNow import searchGoogle
                    searchGoogle(query)
                elif "youtube" in query:
                    from SearchNow import searchYoutube
                    searchYoutube(query)
                elif "wikipedia" in query:
                    from SearchNow import searchWikipedia
                    searchWikipedia(query)

                elif "news" in query:
                    from NewsRead import latestnews
                    latestnews()

                elif "calculate" in query:
                    from Calculatenumbers import WolfRamAlpha
                    from Calculatenumbers import Calc
                    query = query.replace("calculate","")
                    query = query.replace("jarvis","")
                    Calc(query)

                elif "whatsapp" in query:
                    from Whatsapp import sendMessage
                    sendMessage()
                    
                elif "temperatura" in query:
                    search = "temperature in Manaus"
                    url = f"https://www.google.com/search?q={search}"
                    r  = requests.get(url)
                    data = BeautifulSoup(r.text,"html.parser")
                    temp = data.find("div", class_ = "BNeawe").text
                    speak(f"current{search} is {temp}")
                    
                elif "weather" in query:
                    search = "temperature in Manaus"
                    url = f"https://www.google.com/search?q={search}"
                    r  = requests.get(url)
                    data = BeautifulSoup(r.text,"html.parser")
                    temp = data.find("div", class_ = "BNeawe").text
                    speak(f"current{search} is {temp}")

                elif "salve um alarme" in query:
                    print("Exemplo de entrada de tempo:- 10 and 10 and 10")
                    speak("Defina o horário")
                    a = input("Por favor, diga a hora :- ")
                    alarm(a)
                    speak("Feito, senhor")

                elif "que horas são" in query:
                    strTime = datetime.datetime.now().strftime("%H:%M")    
                    speak(f"Senhor, são {strTime}")
                elif "finalmente dormir" in query:
                    speak("Indo dormir, senhor")
                    exit()

                elif "lembrar disso" in query:
                    rememberMessage = query.replace("remember that","")
                    rememberMessage = query.replace("jarvis","")
                    speak(""+rememberMessage)
                    remember = open("Remember.txt","a")
                    remember.write(rememberMessage)
                    remember.close()
                elif "what do you remember" in query:
                    remember = open("Remember.txt","r")
                    speak("You told me to remember that" + remember.read())

                elif "desligar o sistema" in query:
                    speak("Tem certeza de que deseja desligar?")
                    shutdown = input("Deseja desligar seu computador? (sim/não)")
                    if shutdown == "sim":
                        os.system("shutdown /s /t 1")

                    elif shutdown == "não":
                        break

                for topic in relay_topics:
                    alias = topic_aliases[topic]
                    
                if f"acender {alias}" in query:
                    client.publish(topic, "1")
                    speak(f"Ligando o {alias}")
                    
                elif f"apagar {alias}" in query:
                    client.publish(topic, "0")
                    speak(f"Apagando o {alias}")