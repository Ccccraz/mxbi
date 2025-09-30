from concurrent.futures import Future, ThreadPoolExecutor
from threading import Event
from time import sleep

import numpy as np
import pyaudio

SAMPLE_RATE = 44100


class APlayer:
    def __init__(self):
        self._executor = ThreadPoolExecutor(max_workers=1)
        self._player = pyaudio.PyAudio()
        self._stop_event = Event()

    def _generate_tone(
        self, frequency: float, duration: float, ampplitude: float
    ) -> np.ndarray:
        """generate a tone with a given frequency and duration

        Args:
            frequency (float): frequency of the tone
            duration (float): duration of the tone

        Returns:
            np.ndarray: time series of the tone
        """
        # generate time series
        t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)

        # generate sine wave
        tone = ampplitude * np.sin(2 * np.pi * frequency * t)

        # convert to 16-bit PCM format
        tone = (tone * 32767).astype(np.int16)

        return tone

    def _generate_alternating_tone(
        self,
        freq1: float,
        freq2: float,
        switch_interval: float,
        total_duration: float,
        amplitude: float,
    ) -> np.ndarray:
        """
        生成在两个频率之间交替的音频波形

        Args:
            freq1 (float): 第一个频率 Hz
            freq2 (float): 第二个频率 Hz
            switch_interval (float): 每个频率持续的时间 (秒)
            total_duration (float): 总的音频长度 (秒)
            amplitude (float): 振幅 (0~1)

        Returns:
            np.ndarray: 拼接好的 PCM 16 位波形
        """
        n_switches = int(total_duration // switch_interval)  # 需要切换的次数
        tones = []

        for i in range(n_switches):
            freq = freq1 if i % 2 == 0 else freq2
            t = np.linspace(
                0, switch_interval, int(SAMPLE_RATE * switch_interval), endpoint=False
            )
            tone = amplitude * np.sin(2 * np.pi * freq * t)
            tone = (tone * 32767).astype(np.int16)
            tones.append(tone)

        return np.concatenate(tones)

    def _play(
        self,
        frequency: float,
        duration: float,
        ampplitude: float,
        repeat: int,
        interval: float,
    ) -> bool:
        """
        返回值:
            True  -> 正常播放完毕
            False -> 播放过程中被取消
        """
        try:
            tone = self._generate_tone(frequency, duration, ampplitude)
            stream = self._player.open(
                format=pyaudio.paInt16, channels=1, rate=SAMPLE_RATE, output=True
            )

            chunk_size = 1024
            for _ in range(repeat):
                for start in range(0, len(tone), chunk_size):
                    if self._stop_event.is_set():
                        stream.stop_stream()
                        stream.close()
                        return False
                    end = start + chunk_size
                    stream.write(tone[start:end].tobytes())

                if interval > 0:
                    for _ in range(int(interval * 100)):
                        if self._stop_event.is_set():
                            stream.stop_stream()
                            stream.close()
                            return False
                        sleep(0.01)

            stream.stop_stream()
            stream.close()
            return True
        except Exception as e:
            raise e
        finally:
            self._stop_event.clear()

    def _play_alternating(
        self,
        freq1: float,
        freq2: float,
        switch_interval: float,
        total_duration: float,
        amplitude: float,
        repeat: int,
        interval: float,
    ) -> bool:
        """
        播放交替音调，支持取消
        
        返回值:
            True  -> 正常播放完毕
            False -> 播放过程中被取消
        """
        try:
            tone = self._generate_alternating_tone(
                freq1, freq2, switch_interval, total_duration, amplitude
            )
            stream = self._player.open(
                format=pyaudio.paInt16, channels=1, rate=SAMPLE_RATE, output=True
            )

            chunk_size = 1024
            for _ in range(repeat):
                # 分块播放音频数据，以便检查取消信号
                for start in range(0, len(tone), chunk_size):
                    if self._stop_event.is_set():
                        stream.stop_stream()
                        stream.close()
                        return False
                    end = start + chunk_size
                    stream.write(tone[start:end].tobytes())

                # 处理重复间隔
                if interval > 0:
                    for _ in range(int(interval * 100)):
                        if self._stop_event.is_set():
                            stream.stop_stream()
                            stream.close()
                            return False
                        sleep(0.01)

            stream.stop_stream()
            stream.close()
            return True
        except Exception as e:
            raise e
        finally:
            self._stop_event.clear()

    def cancel(self):
        self._stop_event.set()

    def play_tone_async(
        self,
        frequency: float,
        duration: float,
        amplitude: float = 1.0,
        repeat: int = 1,
        interval: float = 0.0,
    ) -> Future[bool]:
        """
        async play a tone

        args:
            frequency (float): frequency of the tone, unit Hz
            duration (float): duration of the tone, unit second
        """
        return self._executor.submit(
            self._play, frequency, duration, amplitude, repeat, interval
        )

    def play_alternating_tone_async(
        self,
        freq1: float,
        freq2: float,
        switch_interval: float,
        total_duration: float,
        amplitude: float = 1.0,
        repeat: int = 1,
        interval: float = 0.0,
    ) -> Future[bool]:
        """
        异步播放两个频率之间交替的音频，支持取消
        
        Args:
            freq1 (float): 第一个频率 Hz
            freq2 (float): 第二个频率 Hz
            switch_interval (float): 每个频率持续的时间 (秒)
            total_duration (float): 总的音频长度 (秒)
            amplitude (float): 振幅 (0~1)
            repeat (int): 重复次数
            interval (float): 重复间隔 (秒)
            
        Returns:
            Future[bool]: True表示正常完成，False表示被取消
        """
        return self._executor.submit(
            self._play_alternating, 
            freq1, freq2, switch_interval, total_duration, amplitude, repeat, interval
        )

    def __del__(self) -> None:
        self._player.terminate()
        self._executor.shutdown()


if __name__ == "__main__":
    # 测试单音调播放
    # tone_gen = APlayer()
    # try:
    #     future = tone_gen.play_tone_async(2000, 0.5, 1, 4, 0.5)
    #     # 可以在播放过程中取消
    #     # tone_gen.cancel()
    #     result = future.result()  # True 或 False
    #     print(f"Single tone result: {result}")
    # except Exception as e:
    #     print(f"Error: {e}")

    # 测试交替音调播放
    tone_gen = APlayer()
    try:
        # 在 2000Hz 和 1000Hz 之间交替, 每 0.25 秒切换, 总时长 3 秒
        future = tone_gen.play_alternating_tone_async(
            2000, 1000, 0.25, 3.0, amplitude=1.0, repeat=2, interval=0.5
        )
        
        # 可以在播放过程中取消
        # import threading
        # def cancel_after_delay():
        #     sleep(2)
        #     tone_gen.cancel()
        # threading.Thread(target=cancel_after_delay).start()
        
        result = future.result()  # True 或 False
        print(f"Alternating tone result: {result}")
    except Exception as e:
        print(f"Error: {e}")