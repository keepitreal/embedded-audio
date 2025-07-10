import os
import numpy as np

def create_file(directory, filename, content=""):
    os.makedirs(directory, exist_ok=True)
    file_path = os.path.join(directory, filename)
    with open(file_path, 'w') as f:
        f.write(content)
    return file_path

def stereo_to_mono(stereo_data, bit_depth=32):
    """Convert stereo PCM audio to mono by taking left channel only"""
    if bit_depth == 16:
        # Convert stereo bytes to numpy array of int16
        stereo = np.frombuffer(stereo_data, dtype='<i2')  # little-endian int16
        mono = stereo[::2]  # take left channel only
        return mono.tobytes()
    elif bit_depth == 32:
        # Convert stereo bytes to numpy array of int32
        stereo = np.frombuffer(stereo_data, dtype='<i4')  # little-endian int32
        mono = stereo[::2]  # take left channel only
        return mono.tobytes()
    else:
        raise ValueError(f"Unsupported bit depth: {bit_depth}")
