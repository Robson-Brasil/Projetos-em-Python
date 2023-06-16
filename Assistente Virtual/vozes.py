import pyttsx3

# Inicializa o mecanismo de síntese de voz
engine = pyttsx3.init()

# Obtém todas as vozes disponíveis
voices = engine.getProperty('voices')

# Imprime informações sobre cada voz
for voice in voices:
    print("ID:", voice.id)
    print("Name:", voice.name)
    print("Languages:", voice.languages)
    print("Gender:", voice.gender)
    print("Age:", voice.age)
    print("\n")

# Fecha o mecanismo de síntese de voz
engine.stop()
