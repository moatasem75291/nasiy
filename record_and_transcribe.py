import sounddevice as sd
from scipy.io.wavfile import write
import tempfile
import requests
import os
import dotenv
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
dotenv.load_dotenv()

API_URL = os.getenv("HUGGINGFACE_URL_MODEL")
headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API')}"}


class AudioRecorder:
    """
    Class to record audio from the microphone and save it to a temporary file.
    """

    def __init__(self, duration=5, fs=16000):
        self.duration = duration
        self.fs = fs

    def record_audio(self) -> bytes:
        """Record audio from the microphone."""
        print("Recording... Press Ctrl+C to stop.")
        try:
            audio = sd.rec(
                int(self.duration * self.fs),
                samplerate=self.fs,
                channels=1,
                dtype="int16",
            )
            sd.wait()
            print("Recording complete.")
            return audio
        except Exception as e:
            print(f"Error during recording: {e}")
            return None

    def save_audio(self, audio) -> str:
        """Save the recorded audio to a temporary file."""
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
            write(temp_audio.name, self.fs, audio)
            return temp_audio.name


class AudioTranscriber:
    """
    Class to transcribe audio using the Hugging Face API.
    """

    def transcribe_audio(self, audio_path) -> str:
        """Transcribe audio using the Hugging Face API."""
        with open(audio_path, "rb") as f:
            data = f.read()
        response = requests.post(API_URL, headers=headers, data=data)
        if response.status_code == 200:
            return response.json().get("text", "")
        else:
            print(f"Error during transcription: {response.status_code}")
            return ""
