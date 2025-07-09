import time
import util
import wave
import alsaaudio

class AudioManager:
    """Audio recording and playback manager using ALSA"""

    def __init__(self):
        self.recording = False
        self.device = "default"

    def list_devices(self):
        """List available audio devices"""
        print("Available audio devices:")
        for device in alsaaudio.pcms(alsaaudio.PCM_CAPTURE):
            print(device)

    def list_cards(self):
        """List available audio cards with their indices"""
        print("Available audio cards:")
        cards = alsaaudio.cards()
        for i, card in enumerate(cards):
            print(f"Card {i}: {card}")
        return cards

    def start_recording(self):
        """Start recording audio from the default device"""
        timestamp = time.time()
        filename = f"input_{timestamp}.wav"
        filepath = util.create_file("recordings", filename)

        self.recording = True
        print("Recording started on device:", self.device, "saving to:", filepath)

        # Configure the wave file
        file = wave.open(filepath, 'wb')
        file.setnchannels(2)  # Stereo recording
        file.setsampwidth(4) # PCM_FORMAT_S32_LE (32-bit = 4 bytes)
        file.setframerate(16000)

        # Open the device in non-blocking capture mode
        inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NONBLOCK, 
                           channels=2, rate=16000, format=alsaaudio.PCM_FORMAT_S32_LE, 
                           periodsize=160, device='hw:0,0')

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