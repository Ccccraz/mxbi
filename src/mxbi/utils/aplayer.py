import numpy as np
import pyaudio
from numpy.typing import NDArray
from pydantic import BaseModel
from concurrent.futures import Future, ThreadPoolExecutor
from time import sleep


class ToneConfig(BaseModel):
    frequency: int
    duration: int


SAMPLE_RATE = 44100


class APlayer:
    def __init__(self):
        self._executor = ThreadPoolExecutor(1)
        self._player = pyaudio.PyAudio()
        self._stop = False

    def _gen_unit(self, tone_config: ToneConfig) -> NDArray[np.int16]:
        frequency = tone_config.frequency
        duration = tone_config.duration / 1000

        t: NDArray[np.float64] = np.linspace(
            0, duration, int(SAMPLE_RATE * duration), endpoint=False
        )

        tone: NDArray[np.float64] = np.sin(2 * np.pi * frequency * t)
        fade_samples = int(4.5 * SAMPLE_RATE / 1000)
        samples = len(tone)

        fade_samples = min(fade_samples, samples // 2)

        envelope = np.ones(samples)
        envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
        envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)

        tone = tone * envelope

        max_val = np.iinfo(np.int16).max

        return (tone * max_val).astype(np.int16)

    def generate_tone(
        self, tone_config: list[ToneConfig], times: int
    ) -> NDArray[np.int16]:
        tone_unit = np.concatenate([self._gen_unit(cfg) for cfg in tone_config])

        return np.tile(tone_unit, times)

    def _play_callback(self, in_data, frame_count, time_info, status):
        start = self._pos
        end = start + frame_count * 2
        chunk = self._data[start:end]
        self._pos = end

        if self._pos >= len(self._data):
            return (chunk, pyaudio.paComplete)
        else:
            return (chunk, pyaudio.paContinue)

    def _play(self, tone: NDArray[np.int16]) -> bool:
        self._data = tone.tobytes()
        self._pos = 0

        self._stream = self._player.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=SAMPLE_RATE,
            output=True,
            stream_callback=self._play_callback,
        )

        while self._stream.is_active():
            sleep(0.1)

        if self._stop:
            self._stop = False
            return False
        else:
            return True

    def play(self, tone: NDArray[np.int16]) -> Future[bool]:
        return self._executor.submit(self._play, tone)

    def stop(self) -> None:
        if self._stream.is_active():
            self._stream.stop_stream()

    def __del__(self) -> None:
        self._player.terminate()


if __name__ == "__main__":
    player = APlayer()

    freq_1 = ToneConfig(frequency=1000, duration=100)
    count = 1

    tone_s = player.generate_tone([freq_1], count)

    player._play(tone_s)
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(12, 4))

    normalized_tone = tone_s / np.iinfo(np.int16).max

    time_axis = np.linspace(0, len(tone_s) / SAMPLE_RATE * 1000, len(tone_s))

    ax.plot(time_axis, normalized_tone)

    ax.set_title(
        f"Waveform - Frequency: {freq_1.frequency}Hz, Duration: {freq_1.duration}ms"
    )
    ax.set_xlabel("Time (ms)")
    ax.set_ylabel("Amplitude")
    ax.grid(True)

    ax.text(
        0.02,
        0.95,
        f"Frequency: {freq_1.frequency}Hz",
        transform=ax.transAxes,
        bbox=dict(facecolor="white", alpha=0.8),
        verticalalignment="top",
    )

    plt.tight_layout()
    plt.show()
