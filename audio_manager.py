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
        file.setsampwidth(2) # PCM_FORMAT_S16_LE
        file.setframerate(44100)

        # Open the device in non-blocking capture mode
        devices_to_try = [
            ('default', None),
            ('hw:CARD=wm8960soundcard,DEV=0', None),
            ('sysdefault:CARD=wm8960soundcard', None),
            (None, 0)  # cardindex=0 creates 'hw:0'
        ]
        
        inp = None
        for device_name, card_idx in devices_to_try:
            try:
                print(f"Trying device: {device_name if device_name else f'cardindex={card_idx}'}")
                
                if card_idx is not None:
                    inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NONBLOCK, 
                                       channels=2, rate=44100, format=alsaaudio.PCM_FORMAT_S16_LE, 
                                       periodsize=160, cardindex=card_idx)
                else:
                    inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NONBLOCK, 
                                       channels=2, rate=44100, format=alsaaudio.PCM_FORMAT_S16_LE, 
                                       periodsize=160, device=device_name)
                
                print(f"Success! Using device: {device_name if device_name else f'cardindex={card_idx}'}")
                print("Device info:", inp.info())
                break
                
            except alsaaudio.ALSAAudioError as e:
                print(f"Failed with {device_name if device_name else f'cardindex={card_idx}'}: {e}")
                continue
        
        if inp is None:
            print("All devices failed!")
            return

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