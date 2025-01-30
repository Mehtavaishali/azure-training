from dotenv import load_dotenv
from datetime import datetime
import os
import azure.cognitiveservices.speech as speech_sdk

def main():
    try:
        global speech_config
        
        # Load environment variables
        load_dotenv()
        ai_key = os.getenv('SPEECH_KEY')
        ai_region = os.getenv('SPEECH_REGION')
        
        # Configure speech service
        speech_config = speech_sdk.SpeechConfig(subscription=ai_key, region=ai_region)
        print('Ready to use speech service in:', speech_config.region)
        
        # Get spoken input
        command = transcribe_command()
        if command.lower() == 'what time is it?':
            tell_time()
    except Exception as ex:
        print("Error:", ex)

def transcribe_command():
    command = ''
    
    # Configure speech recognition
    audio_config = speech_sdk.AudioConfig(use_default_microphone=True)
    speech_recognizer = speech_sdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    
    print('Speak now...')
    
    # Process speech input
    speech = speech_recognizer.recognize_once_async().get()
    
    if speech.reason == speech_sdk.ResultReason.RecognizedSpeech:
        command = speech.text
        print("Recognized Command:", command)
    else:
        print("Speech Recognition Failed:", speech.reason)
        if speech.reason == speech_sdk.ResultReason.Canceled:
            cancellation = speech.cancellation_details
            print("Cancellation Reason:", cancellation.reason)
            print("Error Details:", cancellation.error_details)
    
    return command

def tell_time():
    now = datetime.now()
    response_text = f'The time is {now.hour}:{now.minute:02d}'
    
    # Configure speech synthesis
    speech_config.speech_synthesis_voice_name = "en-GB-LibbyNeural"
    speech_synthesizer = speech_sdk.SpeechSynthesizer(speech_config=speech_config)
    
    # Synthesize spoken output
    speak = speech_synthesizer.speak_text_async(response_text).get()
    if speak.reason != speech_sdk.ResultReason.SynthesizingAudioCompleted:
        print("Speech Synthesis Failed:", speak.reason)
    
    print(response_text)

if __name__ == "__main__":
    main()
