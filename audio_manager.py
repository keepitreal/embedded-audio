import time
import util
import wave
import alsaaudio

class AudioManager:
    """Audio recording and playback manager using ALSA"""

    def __init__(self):
        self.recording = False
        self.device = "default"

    def start_recording(self):
        """Start recording audio from the default device"""
        timestamp = time.time()
        filename = f"input_{timestamp}.wav"
        filepath = util.create_file("recordings", filename)

        self.recording = True
        print("Recording started on device:", self.device, "saving to:", filepath)

        # Configure the wave file
        file = wave.open(filepath, 'wb')
        file.setnchannels(2)
        file.setsampwidth(2) # PCM_FORMAT_S16_LE
        file.setframerate(44100)

        # Open the device in non-blocking capture mode
        inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NONBLOCK, channels=2, rate=44100, format=alsaaudio.PCM_FORMAT_S16_LE, periodsize=160, device=device)
        inp.setperiodsize(160)

        while self.recording:
            # Read data from the device
            l, data = inp.read()
            if l:
                file.writeframes(data)
            time.sleep(0.001)

        file.close()

    def stop_recording(self):
        """Stop recording audio"""
        self.recording = False
        print("Recording stopped")