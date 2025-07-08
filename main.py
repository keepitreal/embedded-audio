import audio_manager
import threading

def main():
    am = audio_manager.AudioManager()
    am.list_devices()
    am.start_recording()
    threading.Timer(5, am.stop_recording).start()

if __name__ == "__main__":
    main()