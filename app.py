import playsound
import speech_recognition as sr
from gtts import gTTS
import random
import os
import datetime
from base64 import b64decode
import openai
from openai.error import InvalidRequestError
from PIL import Image

API_KEY = YOUR_OPENIA_API_KEY

openai.api_key = API_KEY

def speak(text):
    tts = gTTS(text = text, lang = "tr")
    dosya_ismi = "ses" + str(random.randint(0,999)) + ".mp3"
    tts.save(dosya_ismi)
    playsound.playsound(dosya_ismi)
    os.remove(dosya_ismi)

def record(timeout):
    rec = sr.Recognizer()

    with sr.Microphone() as mic:
        rec.adjust_for_ambient_noise(mic)
        print("AI: Dinliyorum.. (" + str(timeout) + " saniye)")
        sound = rec.listen(mic, phrase_time_limit=timeout)
        print("AI: Süre Doldu")
        tell = ""
        try:
            tell = rec.recognize_google(sound, language="Tr-tr")
            if "Programı kapat" in tell:
                exit()
        except sr.WaitTimeoutError:
            speak("Dinleme zaman aşımına uğradı")
        except sr.UnknownValueError:
            speak("Ne dediğini anlayamadım")
        except sr.RequestError:
            speak("İnternete bağlanamıyorum")
    return tell

def generateImage(prompt, num_image=2, size="512x512", output_format="b64_json"):
    """
    params:
        propt (str):
        num_image (int):
        size (str):
        output_format (str)
    """
    try:
        images = []
        response = openai.Image.create(
            prompt=prompt,
            n=num_image,
            size=size,
            response_format=output_format
        )
        if output_format == "url":
            for image in response["data"]:
                images.append(image.url)
        elif output_format == "b64_json":
            for image in response["data"]:
                images.append(image.b64_json)
        return {"created": datetime.datetime.fromtimestamp(response["created"]), "images": images}
    except InvalidRequestError as e: 
        print(e)

def createImage(text): 
    """
    params:
        text (str):
    """
    print(text + " resmi oluşturuluyor...")
    response = generateImage(text)
    prefix = "aiApp"
    for index, image in enumerate(response["images"]):
        file_name = f'{prefix}_{str(random.randint(0,999))}.jpg'
        with open(file_name, "wb") as f:
            f.write(b64decode(image))
            image = Image.open(file_name)
            image.show()
            print("AI: Resim oluşturuldu!")

def completion(text):
    print("İsteğiniz işleniyor...")
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=text,
        temperature=0.9,
        max_tokens=150,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.6,
        stop=[" Human:", " AI:"]
    )
    speak(response.choices[0].text)
    print("AI: " + response.choices[0].text)

choice = ""
timeout = 5

while True:
    if (choice == ""):
        print("AI: Lütfen asistan veya resim diyerek seçim yapınız.")
        speak("Lütfen asistan veya resim diyerek seçim yapınız.")
        text = record(timeout)
        print("Sen: " + text)
        if "asistan" in text:
            choice = "asistan"
        if "resim" in text:
            choice = "resim"
        if "bekleme süresi" in text:
            timeout = int(text.split("bekleme süresi")[1])
            print("AI: Bekleme süresi '"+ str(timeout) + "' saniye olarak ayarlandı.")
    else:
        if (choice == "asistan"):
            print("AI: Merhaba ben asistan, size nasıl yardımcı olabilirim?")
            speak("Merhaba ben asistan, size nasıl yardımcı olabilirim?")
            text = record(timeout)
            print("Sen: " + text)
            if len(text) > 0:
                if "seçim değiştir" in text:
                    choice = ""
                elif "bekleme süresi" in text:
                    timeout = int(text.split("bekleme süresi")[1])
                    print("AI: Bekleme süresi '"+ str(timeout) + "' saniye olarak ayarlandı.")
                else: 
                    completion(text)
        else:
            print("AI: Merhaba oluşturmak istediğin resmi anlatır mısın?")
            speak("Merhaba oluşturmak istediğin resmi anlatır mısın?")
            text = record(timeout)
            print("Sen: " + text)
            if len(text) > 0:
                if "seçim değiştir" in text:
                    choice = ""
                elif "bekleme süresi" in text:
                    timeout = int(text.split("bekleme süresi")[1])
                    print("AI: Bekleme süresi '"+ str(timeout) + "' saniye olarak ayarlandı.")
                else: 
                    createImage(text)
