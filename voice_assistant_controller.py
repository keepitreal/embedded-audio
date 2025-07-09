import time
import threading
from wake_word_detector import WakeWordDetector

class VoiceAssistantController:
    """Main controller for the voice assistant system"""
    
    def __init__(self, wake_words=["hey furby", "hey assistant"]):
        self.wake_words = wake_words
        self.wake_word_detector = None
        self.is_listening = False
        
        # Initialize wake word detector
        self.setup_wake_word_detector()
    
    def setup_wake_word_detector(self):
        """Initialize the wake word detector"""
        try:
            self.wake_word_detector = WakeWordDetector(wake_words=self.wake_words)
            self.wake_word_detector.set_wake_word_callback(self.on_wake_word_detected)
            print("✅ Wake word detector initialized")
        except Exception as e:
            print(f"❌ Error initializing wake word detector: {e}")
            self.wake_word_detector = None
    
    def on_wake_word_detected(self, text):
        """Called when wake word is detected"""
        print(f"🎤 Wake word detected: '{text}'")
        
        # TODO: Add prompt recording here
        # TODO: Add backend communication here
        
        # For now, just log the detection
        print("👂 Continuing to listen for wake words...")
    
    def listen(self):
        """Start the voice assistant listening loop"""
        if not self.wake_word_detector:
            print("❌ Cannot start listening - wake word detector not initialized")
            return
        
        print("🚀 Starting Voice Assistant Controller...")
        print("👂 Listening for wake words:", self.wake_words)
        
        # Start wake word detection
        self.wake_word_detector.start_listening()
        self.is_listening = True
        
        try:
            # Keep the main thread alive
            while self.is_listening:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop the voice assistant"""
        print("🛑 Stopping Voice Assistant Controller...")
        self.is_listening = False
        
        if self.wake_word_detector:
            self.wake_word_detector.stop_listening()
        
        print("✅ Voice Assistant Controller stopped")
