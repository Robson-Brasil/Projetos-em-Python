from pyfirmata import Arduino  # pip install pyfirmata
import pyttsx3  # pip install pyttsx3
import serial
import speech_recognition as sr  # pip install SpeechRecognition
import openai  # pip install openai
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

# MQTT
import paho.mqtt.client as mqtt

# Configurações do MQTT
mqtt_server = "192.168.15.10"
mqtt_port = 1883
mqtt_user = "RobsonBrasil"
mqtt_password = "loboalfa"

# Configuração dos tópicos e aliases
topicos = {
    "ESP32/MinhaCasa/QuartoRobson/Interruptor1/Comando": "luz forte",
    "ESP32/MinhaCasa/QuartoRobson/Interruptor2/Comando": "luz fraca",
    "ESP32/MinhaCasa/QuartoRobson/Interruptor3/Comando": "cooler",
    "ESP32/MinhaCasa/QuartoRobson/Interruptor4/Comando": "relé 4",
    "ESP32/MinhaCasa/QuartoRobson/Interruptor5/Comando": "relé 5",
    "ESP32/MinhaCasa/QuartoRobson/Interruptor6/Comando": "relé 6",
    "ESP32/MinhaCasa/QuartoRobson/Interruptor7/Comando": "relé 7",
    "ESP32/MinhaCasa/QuartoRobson/Interruptor8/Comando": "relé 8"
}

config_assistente = {
    "porta_arduino": "COM100",
    "pino": 4,
    "assistente_falante": True,
    "com_arduino": False,
    "entrada_por_texto": False,
    "lingua": "pt-BR",
    "voz": 0,
    # caso nao queira falar "assistente" ou "Chat GPT"
    "sem_palavra_ativadora": True,
    "sem_palavra_ativadora_chatgpt": True,
    # ajusta ruido do ambiente
    "ajustar_ambiente_noise": True
}

# Inicializar o objeto de síntese de fala
engine = pyttsx3.init()

# Configurar o cliente MQTT
client = mqtt.Client()
client.username_pw_set(mqtt_user, mqtt_password)
client.connect(mqtt_server, mqtt_port, 60)

def falar(texto, engine, voices, voz_escolhida=0):
    engine.setProperty('voice', voices[voz_escolhida].id)
    # falando
    engine.say(texto)
    engine.runAndWait()
    engine.stop()

def generate_answer(messages):
    try:
        response = openai.ChatCompletion.create(
            # model="gpt-4",
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=1000,
            temperature=0.9,
            top_p=0.5,
            frequency_penalty=0.25,
            presence_penalty=0.25
        )
        return [response.choices[0].message.content, response.usage]
    except Exception as e:
        print("Deu ruim", e)
        return ["", ""]

def zerarMensagens():
    return [{"role": "system", "content": "Seu nome é Robson Brasil"}]

def on_connect(client, userdata, flags, rc):
    print("Conectado ao Broker MQTT")
    # Inscreva-se nos tópicos MQTT ao se conectar
    for topic in topicos.keys():
        client.subscribe(topic)

def on_message(client, userdata, msg):
    mensagem = msg.payload.decode()
    print("Mensagem recebida:", mensagem)
    # Verifique se a mensagem corresponde a um tópico conhecido
    if msg.topic in topicos.keys():
        alias = topicos[msg.topic]
        print("Alias correspondente:", alias)
        # Processar ação com base no alias
        if alias == "luz forte":
            # Lógica para acionar o relé correspondente
            print("Acionando luz forte...")
        elif alias == "luz fraca":
            # Lógica para acionar o relé correspondente
            print("Acionando luz fraca...")
        elif alias == "cooler":
            # Lógica para acionar o relé correspondente
            print("Acionando cooler...")
        elif alias.startswith("relé"):
            # Obter o número do relé do alias
            rele_num = int(alias.split(" ")[-1])
            # Lógica para acionar o relé correspondente
            print(f"Acionando relé {rele_num}...")
    else:
        print("Tópico desconhecido:", msg.topic)

def main():
    if config_assistente["com_arduino"]:
        try:
            board = Arduino(config_assistente["porta_arduino"])
        except:
            print("Nao encontrei arduino na porta", config_assistente["porta_arduino"])
            return "Encerrando"

    # Initialize the API key
    f = open('chat_key.json')
    chave = json.load(f)
    openai.api_key = chave['api_key']

    # falar
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('rate', 180)  # velocidade 120 = lento
    for indice, vozes in enumerate(voices):  # listar vozes
        print(indice, vozes.name)
    print("Voz escolhida", config_assistente["voz"], voices[config_assistente["voz"]].name)
    print("")

    # ouvir
    r = sr.Recognizer()
    mic = sr.Microphone()

    sair = {"sair", "jarvis desligar"}
    chamar_assistente = {"jarvis"}
    chamar_assistente_ChatGPT = {"gpt", "chatgpt", "chat gpt"}
    cancelar = ("cancela", "cancelar")

    comando1 = {"ligar luz"}
    comando2 = {"desligar luz"}
    comandos = [comando1, comando2]

    comecar = set()
    comecar.update(sair)
    comecar.update(chamar_assistente)
    comecar.update(chamar_assistente_ChatGPT)

    falar("Robson Brasil", engine, voices, config_assistente["voz"])

    # Configuração do cliente MQTT
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    # Conexão ao Broker MQTT
    broker_address = "mqtt.example.com"  # Substitua pelo endereço do seu Broker MQTT
    broker_port = 1883  # Substitua pela porta do seu Broker MQTT (padrão: 1883)
    client.connect(broker_address, broker_port)

    # Loop de monitoramento do cliente MQTT
    client.loop_start()

    while True:
        print("")
        print("Chamadas", comecar)
        print("Comandos", comandos)
        print("")
        if config_assistente["entrada_por_texto"]:
            comando_recebido = input("Perguntar pro ChatGPT (\"sair\"): ")
        else:
            # Ask a question
            with mic as fonte:
                if config_assistente["ajustar_ambiente_noise"]:
                    r.adjust_for_ambient_noise(fonte)
                    ajustar_ambiente_noise = False
                print("Fale alguma coisa")
                audio = r.listen(fonte)
                print("Enviando para reconhecimento")

                try:
                    comando_recebido = r.recognize_google(audio, language=config_assistente["lingua"])
                except:
                    print("Problemas com o reconhecimento")
                    comando_recebido = ""
                print("############ Ouvi:", comando_recebido)

        comecodafrase = ""
        for espressao in comecar:
            if comando_recebido.lower().startswith(espressao):
                comecodafrase = espressao.lower()

        if comecodafrase in sair:
            print(comando_recebido, "Saindo.")
            if config_assistente["assistente_falante"]:
                falar("Desligando", engine, voices, config_assistente["voz"])
            break
        elif comando_recebido == "" or comando_recebido.lower().endswith(cancelar):
            print("!!! Sem som, texto ou cancelou !!!", comando_recebido)
            continue
        elif comecodafrase in chamar_assistente or config_assistente["sem_palavra_ativadora"]:
            if len(comecodafrase) > 0:
                comando_recebido = comando_recebido[len(comecodafrase) + 1:].lower()
            elif config_assistente["sem_palavra_ativadora"]:
                mensagem = comando_recebido
            print("comando_recebido", comando_recebido)
            if comando_recebido in comando1:
                if (config_assistente["assistente_falante"]):
                    falar("Vai ligar", engine, voices, config_assistente["voz"])
                if config_assistente["com_arduino"]:
                    board.digital[config_assistente["pino"]].write(1)
            elif comando_recebido in comando2:
                if (config_assistente["assistente_falante"]):
                    falar("Vai Desligar", engine, voices, config_assistente["voz"])
                if config_assistente["com_arduino"]:
                    board.digital[config_assistente["pino"]].write(0)
        elif comecodafrase in chamar_assistente_ChatGPT or config_assistente["sem_palavra_ativadora_chatgpt"]:
            if len(comecodafrase) > 0:
                mensagem = comando_recebido[len(comecodafrase) + 1:]
            elif config_assistente["sem_palavra_ativadora_chatgpt"]:
                mensagem = comando_recebido
            print("comando_recebido", mensagem)
            mensagens = zerarMensagens()
            mensagens.append({"role": "user", "content": str(mensagem)})
            answer = generate_answer(mensagens)

            resposta = answer[0]
            preco = answer[1]

            print("ChatGPT:", resposta)
            if (config_assistente["assistente_falante"]):
                falar(resposta, engine, voices, config_assistente["voz"])
        
        elif comando_recebido.lower().startswith("luz forte"):
            if config_assistente["com_arduino"]:
                board.digital[config_assistente["pino"]].write(1)
                print("Ligando luz forte")
        
        elif comando_recebido.lower().startswith("luz fraca"):
            if config_assistente["com_arduino"]:
                board.digital[config_assistente["pino"]].write(0)
                print("Desligando luz fraca")
        
        elif comando_recebido.lower().startswith("cooler"):
            if config_assistente["com_arduino"]:
                # Acione o relé do cooler aqui
                print("Acionando o cooler")
        
        elif comando_recebido.lower().startswith("relé 4"):
            if config_assistente["com_arduino"]:
                # Acione o relé 4 aqui
                print("Acionando o relé 4")
        
        elif comando_recebido.lower().startswith("relé 5"):
            if config_assistente["com_arduino"]:
                # Acione o relé 5 aqui
                print("Acionando o relé 5")
        
        elif comando_recebido.lower().startswith("relé 6"):
            if config_assistente["com_arduino"]:
                # Acione o relé 6 aqui
                print("Acionando o relé 6")
        
        elif comando_recebido.lower().startswith("relé 7"):
            if config_assistente["com_arduino"]:
                # Acione o relé 7 aqui
                print("Acionando o relé 7")
        
        elif comando_recebido.lower().startswith("relé 8"):
            if config_assistente["com_arduino"]:
                # Acione o relé 8 aqui
                print("Acionando o relé 8")
        
        else:
            print("Comando não reconhecido:", comando_recebido)

    return "Fim"

if __name__ == '__main__':
    texto = main()
    print(texto)