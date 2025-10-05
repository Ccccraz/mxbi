import numpy as np
import pyaudio
from numpy.typing import NDArray
from pydantic import BaseModel
from concurrent.futures import Future, ThreadPoolExecutor
from mxbi.utils.audio_control import set_master_volume, set_digital_volume
from dataclasses import dataclass
from threading import Event


@dataclass
class StimulusUnit:
    stimulus: NDArray[np.int16]
    stimulus_master_amp: int | None = None
    stimulus_digital_amp: int | None = None


@dataclass
class StimulusUnitConfig:
    freq: int
    duration: int  # ms
    interval: int  # ms
    master_volume: int | None = None
    digital_volume: int | None = None


class ToneConfig(BaseModel):
    frequency: int
    duration: int  # ms


SAMPLE_RATE = 44100


class APlayer:
    def __init__(self):
        self._executor = ThreadPoolExecutor(1)
        self._player = pyaudio.PyAudio()
        self._stop_event = Event()
        self._stream = self._player.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=SAMPLE_RATE,
            output=True,
        )

    def _gen_unit(self, tone_config: ToneConfig) -> NDArray[np.int16]:
        samples = int(SAMPLE_RATE * (tone_config.duration / 1000))
        if samples <= 0:
            return np.zeros(0, dtype=np.int16)

        t = np.arange(samples) / SAMPLE_RATE
        tone = np.sin(2 * np.pi * tone_config.frequency * t)

        fade_samples = min(int(4.5 * SAMPLE_RATE / 1000), samples // 2)
        if fade_samples > 0:
            envelope = np.ones(samples)
            envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
            envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)
            tone *= envelope

        max_val = np.iinfo(np.int16).max
        return (tone * max_val).astype(np.int16)

    def generate_tone(
        self, tone_config: list[ToneConfig], times: int
    ) -> NDArray[np.int16]:
        tone_unit = np.concatenate([self._gen_unit(cfg) for cfg in tone_config])
        return np.tile(tone_unit, times)

    def _build_unit(self, u: StimulusUnitConfig) -> StimulusUnit:
        tone = self.generate_tone(
            [
                ToneConfig(frequency=u.freq, duration=u.duration),
                ToneConfig(frequency=0, duration=u.interval),
            ],
            1,
        )
        return StimulusUnit(
            stimulus=tone,
            stimulus_master_amp=u.master_volume,
            stimulus_digital_amp=u.digital_volume,
        )

    def generate_stimulus_sequence(
        self, unit_configs: list[StimulusUnitConfig], duration: int
    ) -> list[StimulusUnit]:
        unit_durations = [u.duration + u.interval for u in unit_configs]
        cycle_duration = sum(unit_durations)

        k, r = divmod(duration, cycle_duration)

        sequence = [self._build_unit(u) for _ in range(k) for u in unit_configs]

        for u, dur in zip(unit_configs, unit_durations):
            if r >= dur:
                r -= dur
                sequence.append(self._build_unit(u))
            else:
                break

        return sequence

    def _play(self, tones: list[StimulusUnit]) -> bool:
        for tone in tones:
            if (
                tone.stimulus_master_amp is not None
                and tone.stimulus_digital_amp is not None
            ):
                set_master_volume(tone.stimulus_master_amp)
                set_digital_volume(tone.stimulus_digital_amp)

            data = tone.stimulus.tobytes()
            chunk_size = 1024

            offset = 0
            while chunk := data[offset : offset + chunk_size]:
                if self._stop_event.is_set():
                    return False

                self._stream.write(chunk)
                offset += chunk_size

        return True

    def play(self, tone: NDArray[np.int16]) -> Future[bool]:
        return self._executor.submit(self._play, [StimulusUnit(stimulus=tone)])

    def play_with_amp(self, tones: list[StimulusUnit]) -> Future[bool]:
        self._stop_event.clear()
        return self._executor.submit(self._play, tones)

    def stop(self) -> None:
        self._stop_event.set()

    def __del__(self) -> None:
        self._stream.close()
        self._player.terminate()
        self._executor.shutdown(wait=False)


if __name__ == "__main__":
    player = APlayer()

    freq_1 = ToneConfig(frequency=1000, duration=100)
    count = 1

    tone_s = player.generate_tone([freq_1], count)

    player._play([StimulusUnit(stimulus=tone_s)])
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
