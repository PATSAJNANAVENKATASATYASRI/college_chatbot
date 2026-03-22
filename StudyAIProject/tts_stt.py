import pyttsx3
import speech_recognition as sr
import io

# ✅ Text → Speech
def text_to_speech(text: str):
    """Initializes a TTS engine and speaks the given text."""
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 1.0)
    engine.say(text)
    engine.runAndWait()

# ✅ Speech → Text
def speech_to_text(file_obj) -> str:
    """Transcribes speech from an audio file object to text."""
    recognizer = sr.Recognizer()
    with sr.AudioFile(file_obj) as source:
        audio_data = recognizer.record(source)
    return recognizer.recognize_google(audio_data)  # type: ignore

# Example usage
if __name__ == "__main__":
    print("Testing Text-to-Speech...")
    text_to_speech("Hello, this is a test of the text to speech engine.")
    print("TTS test complete.")

    # Note: The speech_to_text function requires a proper audio file object.
    # To test it, you would need to call it with a file like this:
    #
    # try:
    #     with open("sample.wav", "rb") as audio_file:
    #         text = speech_to_text(audio_file)
    #         print(f"Recognized text: {text}")
    # except FileNotFoundError:
    #     print("Create a 'sample.wav' file to test speech-to-text.")
    # except Exception as e:
    #     print(f"An error occurred during STT test: {e}")