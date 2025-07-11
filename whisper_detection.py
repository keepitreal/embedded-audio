import json
import time
import threading
import alsaaudio
import numpy as np
import io
import wave
from faster_whisper import WhisperModel

class WhisperWakeWordDetector:
    """Wake word detection service using Faster-Whisper model"""
    
    def __init__(self, model_path="base", wake_words=["hey furby", "hey assistant"], sample_rate=16000):
        self.model_path = model_path
        self.wake_words = [word.lower() for word in wake_words]
        self.sample_rate = sample_rate
        self.device = "hw:0,0"
        self.is_listening = False
        self.wake_word_callback = None
        
        # Audio buffer for processing chunks
        self.audio_buffer = bytearray()
        self.buffer_duration = 3.0  # Process 3 seconds of audio at a time
        self.buffer_size = int(self.sample_rate * self.buffer_duration * 2)  # 16-bit samples
        
        # Initialize Whisper model
        self.model = None
        self.setup_model()
    
    def setup_model(self):
        """Initialize the Faster-Whisper model"""
        try:
            print(f"🔧 Loading Faster-Whisper model: {self.model_path}")
            # Use CPU by default for Raspberry Pi, can change to "cuda" if GPU available
            self.model = WhisperModel(self.model_path, device="cpu", compute_type="int8")
            print(f"✅ Faster-Whisper model loaded: {self.model_path}")
        except Exception as e:
            print(f"❌ Error loading Faster-Whisper model: {e}")
            print("Make sure faster-whisper is installed: pip install faster-whisper")
            self.model = None
    
    def set_wake_word_callback(self, callback):
        """Set callback function to be called when wake word is detected"""
        self.wake_word_callback = callback
    
    def start_listening(self):
        """Start continuous listening for wake words"""
        if not self.model:
            print("❌ Cannot start listening - model not loaded")
            return
        
        self.is_listening = True
        print("🚀 Starting Whisper wake word detection...")
        print(f"👂 Listening for: {self.wake_words}")
        
        # Start listening in a separate thread
        listening_thread = threading.Thread(target=self._listen_loop)
        listening_thread.daemon = True
        listening_thread.start()
    
    def stop_listening(self):
        """Stop listening for wake words"""
        self.is_listening = False
        print("🛑 Stopping Whisper wake word detection...")
    
    def _listen_loop(self):
        """Main listening loop - runs continuously"""
        try:
            # Open audio device for capture at native 48kHz stereo
            audio = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NONBLOCK,
                                 channels=2, rate=48000, 
                                 format=alsaaudio.PCM_FORMAT_S16_LE,
                                 periodsize=1024, device=self.device)
            
            print("👂 Whisper wake word detection active...")
            
            while self.is_listening:
                # Read audio data
                length, data = audio.read()
                
                if length > 0:
                    # Process 48kHz stereo audio to 16kHz mono
                    processed_data = self._process_audio_for_whisper(data)
                    
                    if processed_data:
                        # Add to buffer
                        self.audio_buffer.extend(processed_data)
                        
                        # Process buffer when it's full enough
                        if len(self.audio_buffer) >= self.buffer_size:
                            self._process_audio_buffer()
                
                time.sleep(0.01)  # Small delay to prevent busy waiting
        
        except Exception as e:
            print(f"❌ Error in Whisper listening loop: {e}")
        finally:
            try:
                audio.close()
            except:
                pass
    
    def _process_audio_for_whisper(self, raw_data):
        """Process 48kHz stereo audio to 16kHz mono for Whisper"""
        try:
            # Convert raw bytes to numpy array (16-bit stereo)
            stereo_data = np.frombuffer(raw_data, dtype=np.int16)
            
            if len(stereo_data) == 0:
                return b''
            
            # Reshape to stereo (2 channels) 
            if len(stereo_data) % 2 != 0:
                # Odd number of samples, trim one
                stereo_data = stereo_data[:-1]
            
            stereo_data = stereo_data.reshape(-1, 2)
            
            # Convert stereo to mono (average channels)
            mono_data = np.mean(stereo_data, axis=1).astype(np.int16)
            
            # Resample from 48000 Hz to 16000 Hz (3:1 ratio)
            # Simple decimation: take every 3rd sample
            if len(mono_data) >= 3:
                resampled_data = mono_data[::3]
            else:
                resampled_data = mono_data
            
            return resampled_data.tobytes()
            
        except Exception as e:
            print(f"⚠️ Whisper audio processing error: {e}")
            return b''
    
    def _process_audio_buffer(self):
        """Process accumulated audio buffer with Whisper"""
        try:
            # Convert buffer to numpy array for Whisper
            audio_np = np.frombuffer(self.audio_buffer[:self.buffer_size], dtype=np.int16)
            
            # Convert to float32 and normalize (Whisper expects float32 in [-1, 1])
            audio_float = audio_np.astype(np.float32) / 32768.0
            
            # Create a temporary WAV file in memory for Whisper
            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(self.sample_rate)  # 16kHz
                wav_file.writeframes(self.audio_buffer[:self.buffer_size])
            
            wav_buffer.seek(0)
            
            # Transcribe with Whisper
            segments, info = self.model.transcribe(
                wav_buffer,
                language="en",  # Force English for better performance
                beam_size=1,    # Fast beam size for real-time
                best_of=1,      # Single candidate for speed
                temperature=0.0 # Deterministic output
            )
            
            # Process segments and check for wake words
            for segment in segments:
                text = segment.text.lower().strip()
                if text:
                    print(f"🎤 Whisper heard: {text}")
                    
                    # Check for wake words
                    if self._contains_wake_word(text):
                        print(f"🎯 Whisper wake word detected: {text}")
                        if self.wake_word_callback:
                            self.wake_word_callback(text)
            
            # Shift buffer - keep last 1 second for overlap
            overlap_size = int(self.sample_rate * 1.0 * 2)  # 1 second * 16-bit
            self.audio_buffer = self.audio_buffer[self.buffer_size - overlap_size:]
            
        except Exception as e:
            print(f"⚠️ Whisper processing error: {e}")
            # Clear buffer on error
            self.audio_buffer.clear()
    
    def _contains_wake_word(self, text):
        """Check if text contains any of the wake words"""
        for wake_word in self.wake_words:
            if wake_word in text:
                return True
        return False

# Example usage
if __name__ == "__main__":
    def on_wake_word(text):
        print(f"🔔 Whisper wake word callback triggered: {text}")
    
    # Create detector with different model sizes:
    # "tiny", "base", "small", "medium", "large-v3"
    # Smaller models are faster, larger models are more accurate
    detector = WhisperWakeWordDetector(model_path="base")
    detector.set_wake_word_callback(on_wake_word)
    detector.start_listening()
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        detector.stop_listening()
        print("🛑 Whisper wake word detection stopped") 