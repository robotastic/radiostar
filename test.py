import numpy as np
import wave

samples = np.fromfile("raw_2021-11-24-21-02-32_162450000.iq",  dtype=np.float32)
d_max_sample_val = 0x7FFF
d_min_sample_val = -0x7FFF
d_normalize_fac = d_max_sample_val
samples *= d_max_sample_val
np.clip(samples,d_min_sample_val ,d_max_sample_val)
samples = np.round(samples)
samples_16 = samples.astype(np.int16)
print(samples_16)


# Convert to (little-endian) 16 bit integers.
audio = (samples * (2 ** 15 - 1)).astype("<h")

with wave.open("sound1.wav", "w") as f:
    # 2 Channels.
    f.setnchannels(1)
    # 2 bytes per sample.
    f.setsampwidth(2)
    f.setframerate(48000)
    f.writeframes(audio.tobytes())