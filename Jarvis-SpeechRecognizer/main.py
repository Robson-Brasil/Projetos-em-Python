import datetime
import sys
import threading
import time
import webbrowser

import keyboard
import paho.mqtt.client as mqtt
import pyttsx3
import pywhatkit
import requests
import speech_recognition as sr
import wikipedia

sys.stdout.reconfigure(encoding='utf-8')

# Configurações do MQTT
# ToDo: Alterar os dados do servidor MQTT aqui:
mqtt_server = "192.168.15.10"
mqtt_port = 1883
mqtt_user = "RobsonBrasil"
mqtt_password = "loboalfa"

# Tópicos MQTT para os relés - Esses Tópicos estão na programação do ESP32
# ToDo: Para autoamações residênciais, inclua seu tóipcos MQTT aqui
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

# Dicionário de aliases para os tópicos - Os Aliases, são para serem usados somente aqui no Python
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


# Configuraçoes da voz, timbre, voz, e pausa de fala
def falar(audio):
    rate = texto_fala.getProperty('rate')
    texto_fala.setProperty('rate', 120)  # Trocar a velocidade da voz
    voices = texto_fala.getProperty('voices')
    texto_fala.setProperty('voice', voices[3].id)  # Trocar as vozes
    texto_fala.say(audio)
    texto_fala.runAndWait()
    time.sleep(0.5)  # Adiciona uma pausa de 1 segundo após cada fala


# Configuração da hora na qual o assistente fala
def hora():
    Hora: str = datetime.datetime.now().strftime("%#H horas e:%#M minutoss,  .....!")
    falar("Agora são....:  ")
    falar(Hora)


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

    falar("A data de hoje é:" + dia)
    falar("de:" + mes)
    falar("de:" + ano)


# Saudação inicial, isso será dito na inicialização do assistente
def bem_vindo():
    falar("Olá Robson Brasil, bem-vindo de volta,.  !")
    hora()
    data()

    periodo_do_dia = datetime.datetime.now().hour
    if periodo_do_dia >= 6 and periodo_do_dia < 12:
        falar("Bom dia mestre!")
    elif periodo_do_dia >= 12 and periodo_do_dia < 18:
        falar("Boa tarde mestre!")
    elif periodo_do_dia >= 18 and periodo_do_dia <= 24:
        falar("Boa noite mestre!")
        falar("Lua a sua disposição, Diga-me, como posso ajudá-lo?")
    else:
        falar("Mestre, vá dormir, já é de madrugada!")


assistant_active = True


def on_message(message):
    global assistant_active
    payload = message.payload.decode("utf-8")


def microfone():
    texto_fala = pyttsx3.init()

    comando = None  # Added the initialization of 'comando'

    r = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            r.pause_threshold = 1
            r.adjust_for_ambient_noise(source, duration=0.15)  # Ajuste para reduzir o ruído, demora uma pouco mais!
            audio = r.listen(source)
            print("Reconhecendo o Comando")
            comando = r.recognize_google(audio, language='pt-BR')
            comando = comando.lower()
            print(comando)
            if 'jarvis' in comando:
                comando = comando.replace('Lua', '')
                texto_fala.runAndWait()

    except Exception as e:
        print(e)
        # falar(" Por favor, repita. Não entendi.")
        return None

    return comando


# Configuração do cliente MQTT
client = mqtt.Client()
client.username_pw_set(mqtt_user, mqtt_password)
client.connect(mqtt_server, mqtt_port, 60)


# Início da configuração da pausa
def definir_tempo_pausa():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        falar("Diga o tempo de pausa desejado:")
        audio = recognizer.listen(source)
        texto_fala.runAndWait()

    try:
        texto = recognizer.recognize_google(audio, language="pt-BR")
        tempo_pausa = extrair_valor_tempo(
            texto)  # Implemente a função extrair_valor_tempo() para converter a entrada em um valor numérico de tempo.
        falar(f"Tempo de pausa definido como {tempo_pausa} segundos.")
        texto_fala.runAndWait()
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


def falar(mensagem):
    texto_fala.say(mensagem)
    texto_fala.runAndWait()


def stop_assistant(falar_mensagem=True):
    assistant_active = [True]  # Inicialmente, o assistente está ativo
    if falar_mensagem:
        falar("Assistente entrando em pausa....")
        texto_fala.runAndWait()

    tempo_pausa = definir_tempo_pausa()
    if tempo_pausa is None:
        tempo_pausa = 10  # Tempo de pausa padrão em segundos

    def retomar_execucao(assistant_active):
        assistant_active[0] = True

    # Monitorar a tecla "A" e a palavra "ativar" para interromper a pausa e reativar o assistente
    def on_key_press(key):
        if key.name == "=":
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


# Esse comando era pra ser acionado mesmo quando o assistente estivesse em pausa, mas, não consegui fazer funcionar, ainda!
def activate_assistant():
    global assistant_active
    assistant_active = True
    falar("Assistente ativado.")
    texto_fala.runAndWait()


# Comando para desligar o assistente
def shutdown_assistant():
    falar("Desligando o assistente.")
    sys.exit()


# Comando para a previsão do Tempo, aqui será obrigatório o uso de uma API
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
chave_api = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"  # Substitua pela sua chave de API da OpenWeatherMap

# O assistente falar a previsão em si!
previsao = obter_previsao_tempo(localizacao, chave_api)
print(previsao)
falar(previsao)
texto_fala.runAndWait()

if __name__ == "__main__":
    bem_vindo()
    obter_previsao_tempo(localizacao, chave_api)
    texto_fala.runAndWait()

    try:
        while True:

            comando = microfone()

            print("Estou Escutando....")

            if assistant_active:
                comando = microfone()
            if comando is not None:
                comando = comando.lower()

            # ToDo: Adione mais sites aqui!
            sites = [
                ["youtube", "https://www.youtube.com"],
                ["wikipedia", "https://www.wikipedia.com"],
                ["google", "https://www.google.com"],
                ["facebook", "https://www.facebook.com"],
            ]

            for site in sites:
                if comando is not None and f"Abrir o site {site[0]}".lower() in comando:
                    falar(f"Abrindo {site[0]}...")
                    webbrowser.open(site[1])
                    break

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

            elif comando is not None and 'tocar' in comando:
                musica = comando.replace('tocar', '')
                resultado = pywhatkit.playonyt(musica)
                falar('Tocando música')
                texto_fala.runAndWait()

            elif comando is not None and 'procurar no youtube' in comando:
                canal = comando.replace('procurar no youtube', '')
                resultadoCanal = pywhatkit.playonyt(canal)
                falar('Encontrando canal')
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
