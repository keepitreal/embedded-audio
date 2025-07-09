import wave
import alsaaudio

class PlaybackManager:
    """Audio playback manager using ALSA"""

    def __init__(self):
        self.device = "hw:0,0"

    def play_file(self, filepath):
        """Play back audio from a wav file"""
        # Open the wave file for reading
        with wave.open(filepath, 'rb') as file:
            # Get file parameters
            channels = file.getnchannels()
            sample_width = file.getsampwidth()
            framerate = file.getframerate()
            frames = file.getnframes()
            
            # Open the device for playback in blocking mode
            out = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK, alsaaudio.PCM_NORMAL,
                               channels=channels, rate=framerate, format=alsaaudio.PCM_FORMAT_S32_LE,
                               periodsize=160, device=self.device)
            
            # Read and play the file
            while True:
                data = file.readframes(160)
                if not data:
                    break
                
                # Write data to the device (blocking mode handles timing automatically)
                out.write(data)
            
            # Close the device (automatically waits for completion in blocking mode)
            out.close()
