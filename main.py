import recording_manager
import playback_manager
import threading

def main():
    rm = recording_manager.RecordingManager()
    pm = playback_manager.PlaybackManager()

    threading.Timer(5, rm.stop_recording).start()
    filepath = rm.start_recording()
    pm.play_file(filepath)

if __name__ == "__main__":
    main()