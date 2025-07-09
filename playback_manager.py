import time
import wave
import alsaaudio

class PlaybackManager:
    """Audio playback manager using ALSA"""

    def __init__(self):
        self.device = "hw:0,0"

    def play_file(self, filepath):
        """Play back audio from a wav file"""
        print(f"Playing back file: {filepath}")
        
        # Open the wave file for reading
        with wave.open(filepath, 'rb') as file:
            # Get file parameters
            channels = file.getnchannels()
            sample_width = file.getsampwidth()
            framerate = file.getframerate()
            frames = file.getnframes()
            
            print(f"File info: {channels} channels, {sample_width} bytes/sample, {framerate} Hz, {frames} frames")
            
            # Open the device for playback
            out = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK, alsaaudio.PCM_NONBLOCK,
                               channels=channels, rate=framerate, format=alsaaudio.PCM_FORMAT_S32_LE,
                               periodsize=160, device=self.device)
            
            # Read and play the file
            while True:
                data = file.readframes(160)
                if not data:
                    break
                
                # Write data to the device
                out.write(data)
                time.sleep(0.001)
            
            # Wait for playback to complete
            out.drain()
            print("Playback completed")
