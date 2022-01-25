from flask import Flask, render_template, url_for, jsonify, request

import towav

import azure.cognitiveservices.speech as speechsdk
import time
import credentials

app = Flask(__name__)
#app.config['JSON_AS_ASCII'] = False

@app.route('/')
def index():
    return render_template('index.html')

#@app.route('/base64_convert')
#def base64_convert():
    #towav.process_audio()

@app.route('/convert_once')
def convert_to_text_once():
    #process audio
    towav.process_audio()
    subscription=credentials.subscription
    region=credentials.region
    speech_config = speechsdk.SpeechConfig(subscription=subscription, region=region)
    audio_config = speechsdk.AudioConfig(filename="temp.wav")

    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    result = speech_recognizer.recognize_once_async().get()
    return result.text

@app.route('/convert_continuous')
def convert_to_text_continuous():
    #process audio
    towav.process_audio()
    
    """performs continuous speech recognition with input from an audio file"""
    subscription=credentials.subscription
    region=credentials.region

    speech_config = speechsdk.SpeechConfig(subscription=subscription, region=region)
    audio_config = speechsdk.AudioConfig(filename="temp.wav")

    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    done = False

    def stop_cb(evt):
        """callback that stops continuous recognition upon receiving an event `evt`"""
        print('CLOSING on {}'.format(evt))
        speech_recognizer.stop_continuous_recognition()
        nonlocal done
        done = True

    all_results = []
    def handle_final_result(evt):
        all_results.append(evt.result.text)

    speech_recognizer.recognized.connect(handle_final_result)
    # Connect callbacks to the events fired by the speech recognizer
    speech_recognizer.recognizing.connect(lambda evt: print('RECOGNIZING: {}'.format(evt)))
    speech_recognizer.recognized.connect(lambda evt: print('RECOGNIZED: {}'.format(evt)))
    speech_recognizer.session_started.connect(lambda evt: print('SESSION STARTED: {}'.format(evt)))
    speech_recognizer.session_stopped.connect(lambda evt: print('SESSION STOPPED {}'.format(evt)))
    speech_recognizer.canceled.connect(lambda evt: print('CANCELED {}'.format(evt)))
    # stop continuous recognition on either session stopped or canceled events
    speech_recognizer.session_stopped.connect(stop_cb)
    speech_recognizer.canceled.connect(stop_cb)

    # Start continuous speech recognition
    speech_recognizer.start_continuous_recognition()
    while not done:
        time.sleep(.5)


    #print("Printing all results:")
    return ' '.join([str(result) for result in all_results])
