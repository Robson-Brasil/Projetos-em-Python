import pyttsx3  # pip install pyttsx3
import speech_recognition as sr  # pip install SpeechRecognition
import openai  # pip instal openai
import json
import sys
import paho.mqtt.client as mqtt  # pip install paho-mqtt

sys.stdout.reconfigure(encoding='utf-8')

config_assistente = {
    "assistente_falante": True,
    "entrada_por_texto": False,
    "lingua": "pt-BR",
    "voz": 3,
    # caso nao queira falar "assistente" ou "Chat GPT"
    "sem_palavra_ativadora": True,
    "sem_palavra_ativadora_chatgpt": True,
    # ajusta ruido do ambiente
    "ajustar_ambiente_noise": True,
}

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
    "ESP32/MinhaCasa/QuartoRobson/Interruptor8/Comando"
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
            engine.say(f"Apagando o {alias}.")
            engine.runAndWait()
            return


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    for topic in config_assistente["relay_topics"].values():
        client.subscribe(topic)


def on_message(client, userdata, msg):
    print("Received message: " + msg.topic + " " + str(msg.payload))


def falar(texto, engine, voices, voz_escolhida=1):
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
    return [{"role": "system", "content": "Seu nome é Assistente do Robson Brasil"}]


def main():

    # Initialize the API key
    f = open('chat_key.json')
    chave = json.load(f)
    openai.api_key = chave['api_key']

    # Configurar o reconhecimento de voz


recognizer = sr.Recognizer()

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

sair = {"sair"}
chamar_assistente = {"Jarvis"}
chamar_assistente_ChatGPT = {"gpt", "chatgpt", "chat gpt", "lâmpada forte"}
cancelar = ("cancela", "cancelar")

comecar = set()
comecar.update(sair)
comecar.update(chamar_assistente)
comecar.update(chamar_assistente_ChatGPT)

falar("Assistente do Robson Brasil Ligando", engine, voices, config_assistente["voz"])

# Configurar o cliente MQTT
client = mqtt.Client()
client.username_pw_set(mqtt_user, mqtt_password)
client.connect(mqtt_server, mqtt_port, 60)
client.loop_start()

assistant_active = True

while True:
    print("")
    print("Chamadas", comecar)
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

if __name__ == '__main__':
    texto = main()
    print(texto)