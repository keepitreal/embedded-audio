import recording_manager
import threading

def main():
    rm = recording_manager.RecordingManager()
    threading.Timer(5, rm.stop_recording).start()
    rm.start_recording()

if __name__ == "__main__":
    main()