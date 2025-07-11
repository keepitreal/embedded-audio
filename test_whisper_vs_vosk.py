#!/usr/bin/env python3
"""
Test script to compare Whisper vs Vosk wake word detection
"""

import time
import threading
from wake_word_detector import WakeWordDetector
from whisper_detection import WhisperWakeWordDetector

class WakeWordComparison:
    """Compare Vosk and Whisper wake word detectors"""
    
    def __init__(self):
        self.vosk_detector = None
        self.whisper_detector = None
        self.vosk_detections = []
        self.whisper_detections = []
    
    def vosk_callback(self, text):
        """Callback for Vosk wake word detection"""
        print(f"🔵 VOSK detected: '{text}'")
        self.vosk_detections.append((time.time(), text))
    
    def whisper_callback(self, text):
        """Callback for Whisper wake word detection"""
        print(f"🟠 WHISPER detected: '{text}'")
        self.whisper_detections.append((time.time(), text))
    
    def start_comparison(self):
        """Start both detectors for comparison"""
        print("🔬 Wake Word Detection Comparison Test")
        print("=" * 50)
        print("This test will run both Vosk and Whisper wake word detectors")
        print("simultaneously to compare their accuracy and speed.")
        print()
        print("Wake words: 'hey furby', 'hey assistant'")
        print("🔵 = Vosk detection")
        print("🟠 = Whisper detection")
        print()
        
        # Initialize detectors
        print("🔧 Initializing Vosk detector...")
        try:
            self.vosk_detector = WakeWordDetector()
            self.vosk_detector.set_wake_word_callback(self.vosk_callback)
            print("✅ Vosk detector ready")
        except Exception as e:
            print(f"❌ Vosk detector failed: {e}")
        
        print("🔧 Initializing Whisper detector...")
        try:
            # Use "tiny" model for faster performance on Pi
            self.whisper_detector = WhisperWakeWordDetector(model_path="tiny")
            self.whisper_detector.set_wake_word_callback(self.whisper_callback)
            print("✅ Whisper detector ready")
        except Exception as e:
            print(f"❌ Whisper detector failed: {e}")
        
        # Start both detectors
        if self.vosk_detector:
            print("🚀 Starting Vosk detection...")
            self.vosk_detector.start_listening()
        
        if self.whisper_detector:
            print("🚀 Starting Whisper detection...")
            self.whisper_detector.start_listening()
        
        print("\n👂 Both detectors are now listening...")
        print("Try saying: 'hey furby' or 'hey assistant'")
        print("Press Ctrl+C to stop and see results")
        print("=" * 50)
    
    def stop_comparison(self):
        """Stop both detectors and show results"""
        print("\n🛑 Stopping detectors...")
        
        if self.vosk_detector:
            self.vosk_detector.stop_listening()
        
        if self.whisper_detector:
            self.whisper_detector.stop_listening()
        
        # Show results
        print("\n📊 COMPARISON RESULTS")
        print("=" * 50)
        print(f"🔵 Vosk detections: {len(self.vosk_detections)}")
        for timestamp, text in self.vosk_detections:
            print(f"   {time.strftime('%H:%M:%S', time.localtime(timestamp))} - '{text}'")
        
        print(f"\n🟠 Whisper detections: {len(self.whisper_detections)}")
        for timestamp, text in self.whisper_detections:
            print(f"   {time.strftime('%H:%M:%S', time.localtime(timestamp))} - '{text}'")
        
        print(f"\n📈 Summary:")
        print(f"   Vosk: {len(self.vosk_detections)} detections")
        print(f"   Whisper: {len(self.whisper_detections)} detections")
        
        if self.vosk_detections and self.whisper_detections:
            print("   Both detectors are working!")
        elif self.vosk_detections:
            print("   Only Vosk detected wake words")
        elif self.whisper_detections:
            print("   Only Whisper detected wake words")
        else:
            print("   No wake words detected by either detector")

def main():
    comparison = WakeWordComparison()
    
    try:
        comparison.start_comparison()
        
        # Keep running until interrupted
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        comparison.stop_comparison()
        print("\n✅ Comparison test completed")

if __name__ == "__main__":
    main() 