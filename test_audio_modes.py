#!/usr/bin/env python3
"""
Test script to check audio device capabilities for mono vs stereo recording
"""

import alsaaudio
import time
import wave
import util

def test_recording_mode(channels, mode_name):
    """Test if the device supports a specific recording mode"""
    print(f"\n🎤 Testing {mode_name} recording (channels={channels})...")
    
    try:
        # Try to open the device with the specified channel count
        inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NONBLOCK,
                           channels=channels, rate=16000, 
                           format=alsaaudio.PCM_FORMAT_S32_LE,
                           periodsize=160, device="hw:0,0")
        
        print(f"✅ {mode_name} recording: Device opened successfully")
        
        # Try to record a short sample
        filename = f"test_{mode_name.lower()}.wav"
        filepath = util.create_file("recordings", filename)
        
        with wave.open(filepath, 'wb') as file:
            file.setnchannels(channels)
            file.setsampwidth(4)  # 32-bit
            file.setframerate(16000)
            
            print(f"   Recording {mode_name} for 2 seconds...")
            start_time = time.time()
            
            while time.time() - start_time < 2.0:
                length, data = inp.read()
                if length > 0:
                    file.writeframes(data)
                time.sleep(0.01)
        
        inp.close()
        print(f"✅ {mode_name} recording: Successfully recorded to {filepath}")
        return True, filepath
        
    except Exception as e:
        print(f"❌ {mode_name} recording: Failed - {e}")
        return False, None

def main():
    print("Audio Device Capability Test")
    print("=" * 40)
    
    # Test stereo recording (we know this works)
    stereo_works, stereo_file = test_recording_mode(2, "Stereo")
    
    # Test mono recording
    mono_works, mono_file = test_recording_mode(1, "Mono")
    
    print("\n" + "=" * 40)
    print("RESULTS:")
    print(f"📊 Stereo (2 channels): {'✅ Supported' if stereo_works else '❌ Not supported'}")
    print(f"📊 Mono (1 channel):   {'✅ Supported' if mono_works else '❌ Not supported'}")
    
    if mono_works and stereo_works:
        print("\n🎯 Your device supports both mono and stereo recording!")
        print("   You can choose either mode based on your needs.")
    elif stereo_works and not mono_works:
        print("\n🎯 Your device only supports stereo recording.")
        print("   You'll need to record in stereo and convert to mono if needed.")
    elif mono_works and not stereo_works:
        print("\n🎯 Your device only supports mono recording.")
    else:
        print("\n❌ Neither mode worked - there may be a device configuration issue.")
    
    # Play back any successful recordings
    if stereo_works or mono_works:
        print("\n🔊 Playing back test recordings...")
        import playback_manager
        pm = playback_manager.PlaybackManager()
        
        if stereo_file:
            print("Playing stereo test...")
            pm.play_file(stereo_file)
            time.sleep(0.5)
            
        if mono_file:
            print("Playing mono test...")
            pm.play_file(mono_file)

if __name__ == "__main__":
    main() 