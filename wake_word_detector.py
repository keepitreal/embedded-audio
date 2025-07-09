import json
import time
import threading
import alsaaudio
import vosk

class WakeWordDetector:
    """Wake word detection service using Vosk model"""
    
    def __init__(self, model_path="vosk-model", wake_words=["hey assistant", "hey furby"], sample_rate=16000):
        self.model_path = model_path
        self.wake_words = [word.lower() for word in wake_words]
        self.sample_rate = sample_rate
        self.device = "hw:0,0"
        self.is_listening = False
        self.wake_word_callback = None
        
        # Initialize Vosk model
        self.model = None
        self.rec = None
        self.setup_model()
    
    def setup_model(self):
        """Initialize the Vosk model"""
        try:
            self.model = vosk.Model(self.model_path)
            self.rec = vosk.KaldiRecognizer(self.model, self.sample_rate)
            print(f"Vosk model loaded from {self.model_path}")
        except Exception as e:
            print(f"Error loading Vosk model: {e}")
            print("Please ensure Vosk model is installed and path is correct")
    
    def set_wake_word_callback(self, callback):
        """Set callback function to be called when wake word is detected"""
        self.wake_word_callback = callback
    
    def start_listening(self):
        """Start continuous listening for wake words"""
        if not self.model:
            print("Cannot start listening - model not loaded")
            return
        
        self.is_listening = True
        print("Starting wake word detection...")
        
        # Start listening in a separate thread
        listening_thread = threading.Thread(target=self._listen_loop)
        listening_thread.daemon = True
        listening_thread.start()
    
    def stop_listening(self):
        """Stop listening for wake words"""
        self.is_listening = False
        print("Stopping wake word detection...")
    
    def _listen_loop(self):
        """Main listening loop - runs continuously"""
        try:
            # Open audio device for capture
            audio = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NONBLOCK,
                                 channels=1, rate=self.sample_rate, 
                                 format=alsaaudio.PCM_FORMAT_S16_LE,
                                 periodsize=1024, device=self.device)
            
            print("Wake word detection active...")
            
            while self.is_listening:
                # Read audio data
                length, data = audio.read()
                
                if length > 0 and self.rec:
                    # Process audio through Vosk
                    if self.rec.AcceptWaveform(data):
                        # Get recognition result
                        result = json.loads(self.rec.Result())
                        text = result.get('text', '').lower()
                        
                        if text:
                            print(f"Heard: {text}")
                            
                            # Check for wake words
                            if self._contains_wake_word(text):
                                print(f"Wake word detected: {text}")
                                if self.wake_word_callback:
                                    self.wake_word_callback(text)
                
                time.sleep(0.01)  # Small delay to prevent busy waiting
        
        except Exception as e:
            print(f"Error in listening loop: {e}")
        finally:
            try:
                audio.close()
            except:
                pass
    
    def _contains_wake_word(self, text):
        """Check if text contains any of the wake words"""
        for wake_word in self.wake_words:
            if wake_word in text:
                return True
        return False

# Example usage
if __name__ == "__main__":
    def on_wake_word(text):
        print(f"Wake word callback triggered: {text}")
    
    detector = WakeWordDetector()
    detector.set_wake_word_callback(on_wake_word)
    detector.start_listening()
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        detector.stop_listening()
        print("Wake word detection stopped") 