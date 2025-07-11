import time
import util
import wave
import alsaaudio
import threading

class RecordingManager:
    """Audio recording manager using ALSA"""

    def __init__(self):
        self.recording = False
        self.device = "hw:0,0"

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

        # Open the device in non-blocking capture mode with a common sample rate
        inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NONBLOCK, 
                           channels=2, rate=16000, format=alsaaudio.PCM_FORMAT_S32_LE, 
                           periodsize=160, device=self.device)
        
        # Check what rate the device actually set

        # Configure the wave file with the actual rate
        file = wave.open(filepath, 'wb')
        file.setnchannels(2)  # Stereo recording
        file.setsampwidth(4) # PCM_FORMAT_S16_LE (16-bit = 2 bytes)
        file.setframerate(16000)  # Use actual rate, not requested rate

        while self.recording:
            # Read data from the device
            l, data = inp.read()
            if l:
                file.writeframes(data)
            time.sleep(0.001)

        # Clean up resources
        file.close()
        inp.close()  # Explicitly close the PCM device
        return filepath

    def stop_recording(self):
        """Stop recording audio"""
        self.recording = False
        print("Recording stopped")

"""
For testing recording and stereo-to-mono conversion:
"""
if __name__ == "__main__":
    import playback_manager
    import wave
    
    # Record audio
    rm = RecordingManager()
    threading.Timer(5, rm.stop_recording).start()
    stereo_filepath = rm.start_recording()
    
    print(f"Stereo recording saved to: {stereo_filepath}")
    
    # Convert stereo to mono and save
    mono_filepath = stereo_filepath.replace('.wav', '_mono.wav')
    
    # Read the stereo file and convert to mono
    with wave.open(stereo_filepath, 'rb') as stereo_file:
        stereo_data = stereo_file.readframes(-1)  # Read all frames
        mono_data = util.stereo_to_mono(stereo_data, bit_depth=32)  # Use 32-bit conversion
        
        # Convert mono back to stereo (duplicate channels) for better device compatibility
        import numpy as np
        mono_samples = np.frombuffer(mono_data, dtype='<i4')
        fake_stereo = np.zeros((len(mono_samples), 2), dtype='<i4')
        fake_stereo[:, 0] = mono_samples  # Left channel
        fake_stereo[:, 1] = mono_samples  # Right channel (duplicate)
        
        # Save as stereo file with identical L/R channels
        with wave.open(mono_filepath, 'wb') as mono_file:
            mono_file.setnchannels(2)  # Stereo (but with identical channels)
            mono_file.setsampwidth(4)  # 32-bit (same as source)
            mono_file.setframerate(16000)
            mono_file.writeframes(fake_stereo.tobytes())
    
    print(f"Mono version saved to: {mono_filepath}")
    
    # Play back both versions
    pm = playback_manager.PlaybackManager()
    
    print("Playing stereo version...")
    pm.play_file(stereo_filepath)
    
    time.sleep(1)
    
    print("Playing mono version...")
    pm.play_file(mono_filepath)