from abc import ABC, abstractmethod
import asyncio
import base64
import queue
import threading

import numpy as np
from loguru import logger

from phonic.client import PhonicAsyncWebsocketClient


class ContinuousAudioInterface(ABC):
    @abstractmethod
    def __init__(
        self,
        client: PhonicAsyncWebsocketClient,
        sample_rate: int = 44100,
    ):
        pass

    @abstractmethod
    def _input_callback(self, indata, frames, time, status):
        pass

    @abstractmethod
    def _start_input_stream(self):
        pass

    @abstractmethod
    def _output_callback(self, indata, frames, time, status):
        pass

    @abstractmethod
    def _start_output_stream(self):
        pass

    @abstractmethod
    async def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def add_audio_to_playback(self, audio_encoded: str):
        pass

    @abstractmethod
    def interrupt_playback(self):
        pass


class BaseContinuousAudioInterface(ContinuousAudioInterface):
    """
    Handles continuous audio streaming
    with simultaneous recording and playback
    """

    def __init__(
        self,
        client: PhonicAsyncWebsocketClient,
        sample_rate=44100,
    ):
        self.client = client
        self.sample_rate = sample_rate
        self.channels = 1
        self.input_dtype = np.int16
        self.output_dtype = np.int16

        self.is_running = False
        self.playback_queue: queue.Queue = queue.Queue()

        self.input_stream = None
        self.output_stream = None

        self.ready_event = asyncio.Event()
        self.main_loop = asyncio.get_event_loop()

    def _start_output_stream(self):
        # Create a persistent buffer to hold leftover audio between callbacks
        self.overflow_buffer = np.array([], dtype=self.output_dtype)

    async def start(self):
        """Start continuous audio streaming"""
        self.is_running = True
        self.ready_event.set()

        # Start audio streams in separate threads
        input_thread = threading.Thread(target=self._start_input_stream)
        output_thread = threading.Thread(target=self._start_output_stream)

        input_thread.daemon = True
        output_thread.daemon = True

        input_thread.start()
        output_thread.start()

    def stop(self):
        """Stop continuous audio streaming"""
        self.is_running = False

        if self.input_stream:
            self.input_stream.close()

        if self.output_stream:
            self.output_stream.close()

    def add_audio_to_playback(self, audio_encoded: str):
        """Add audio data to the playback queue"""
        audio_bytes = base64.b64decode(audio_encoded)
        audio_data = np.frombuffer(audio_bytes, dtype=self.output_dtype)
        self.playback_queue.put(audio_data)

    def interrupt_playback(self):
        with self.playback_queue.mutex:
            self.playback_queue.queue.clear()


class PyaudioContinuousAudioInterface(BaseContinuousAudioInterface):
    """
    Handles continuous audio streaming
    with simultaneous recording and playback using pyaudio
    """

    def __init__(
        self,
        client: PhonicAsyncWebsocketClient,
        sample_rate: int = 44100,
    ):
        super().__init__(client, sample_rate)
        try:
            import pyaudio
        except ImportError:
            logger.error(
                "The 'pyaudio' library is not installed. "
                "Please install it using 'pip install phonic-python[pyaudio]' "
                "to use PyaudioContinuousAudioInterface."
            )
            raise ImportError(
                "The 'pyaudio' library must be installed "
                "for PyaudioContinuousAudioInterface to work. "
                "Install it with: pip install phonic-python[pyaudio]"
            )
        self.p = pyaudio.PyAudio()
        self.p_input_format = pyaudio.paInt16
        self.p_output_format = pyaudio.paInt16
        self.p_flag_continue = pyaudio.paContinue
        self.p_flag_abort = pyaudio.paAbort

    def _input_callback(self, indata, frames, time, status):
        if status:
            logger.warning(f"Input stream status: {status}")

        if not self.is_running:
            return (None, self.p_flag_abort)

        audio_data = np.frombuffer(indata, dtype=self.input_dtype)
        asyncio.run_coroutine_threadsafe(
            self.client.send_audio(audio_data), self.main_loop
        )
        return (None, self.p_flag_continue)

    def _start_input_stream(self):
        """Start audio input stream in a separate thread"""

        self.input_stream = self.p.open(
            format=self.p_input_format,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            stream_callback=self._input_callback,
            frames_per_buffer=int(self.sample_rate * 0.250),
            start=True,
        )

    def _output_callback(self, indata, frames, time, status):
        # pyaudio doesn't use an output callback
        return

    def _start_output_stream(self):
        """Start audio output stream in a separate thread"""

        super()._start_output_stream()

        self.output_stream = self.p.open(
            format=self.p_output_format,
            channels=self.channels,
            rate=self.sample_rate,
            output=True,
            frames_per_buffer=int(self.sample_rate * 0.0625),
            start=True,
        )

        while self.is_running:
            try:
                audio_data = self.playback_queue.get(timeout=0.25)
                self.output_stream.write(audio_data.tobytes())
            except queue.Empty:
                pass

    def stop(self):
        """Stop continuous audio streaming"""
        super().stop()

        self.p.terminate()


class SounddeviceContinuousAudioInterface(BaseContinuousAudioInterface):
    """
    Handles continuous audio streaming
    with simultaneous recording and playback using sounddevice
    """

    def __init__(
        self,
        client: PhonicAsyncWebsocketClient,
        sample_rate: int = 44100,
    ):
        super().__init__(client, sample_rate)
        try:
            import sounddevice as sd
        except ImportError:
            raise ImportError(
                "The 'sounddevice' library must be installed "
                "for audio streaming to work."
            )
        self.sd = sd

    def _input_callback(self, indata, frames, time, status):
        if status:
            logger.warning(f"Input stream status: {status}")

        if not self.is_running:
            return

        audio_data = indata.copy().flatten()
        asyncio.run_coroutine_threadsafe(
            self.client.send_audio(audio_data), self.main_loop
        )

    def _start_input_stream(self):
        """Start audio input stream in a separate thread"""

        self.input_stream = self.sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            callback=self._input_callback,
            dtype=self.input_dtype,
        )
        self.input_stream.start()

    def _output_callback(self, outdata, frames, time, status):
        if status:
            logger.warning(f"Output stream status: {status}")

        if not self.is_running:
            outdata.fill(0)
            return

        try:
            # Check if we have enough audio data
            # (either in overflow or queue)
            total_available = len(self.overflow_buffer)
            queue_chunks = []

            # Peek at queue contents without removing them yet
            while not self.playback_queue.empty() and total_available < frames:
                chunk = self.playback_queue.get_nowait()
                queue_chunks.append(chunk)
                total_available += len(chunk)

            # If we don't have enough data,
            # put chunks back and return silence
            # This will cause the audio system to wait for more data
            if total_available < frames and self.is_running:
                for chunk in reversed(queue_chunks):
                    self.playback_queue.put(chunk, block=False)
                outdata.fill(0)
                return

            # We have enough data, so fill the output buffer
            filled = 0

            # First use overflow buffer
            if len(self.overflow_buffer) > 0:
                use_frames = min(len(self.overflow_buffer), frames)
                outdata[:use_frames, 0] = self.overflow_buffer[:use_frames]
                self.overflow_buffer = self.overflow_buffer[use_frames:]
                filled += use_frames

            # Then use queued chunks
            for chunk in queue_chunks:
                if filled >= frames:
                    # We've filled the output buffer,
                    # store remainder in overflow
                    self.overflow_buffer = np.append(
                        self.overflow_buffer,
                        chunk,
                    )
                else:
                    use_frames = min(len(chunk), frames - filled)
                    cut_chunk = chunk[:use_frames]
                    outdata[filled : filled + use_frames, 0] = cut_chunk

                    if use_frames < len(chunk):
                        # Store remainder in overflow buffer
                        self.overflow_buffer = np.append(
                            self.overflow_buffer, chunk[use_frames:]
                        )
                    filled += use_frames

        except Exception as e:
            logger.error(f"Error in output callback: {e}")
            outdata.fill(0)

    def _start_output_stream(self):
        """Start audio output stream in a separate thread"""

        super()._start_output_stream()

        self.output_stream = self.sd.OutputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            callback=self._output_callback,
            dtype=self.output_dtype,
        )
        self.output_stream.start()

    def stop(self):
        """Stop continuous audio streaming"""
        if self.input_stream:
            self.input_stream.stop()

        if self.output_stream:
            self.output_stream.stop()

        super().stop()
