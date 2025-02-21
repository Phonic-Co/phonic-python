import asyncio
import queue
import threading

from loguru import logger
import numpy as np

from phonic.client import PhonicAsyncWebsocketClient


class ContinuousAudioInterface:
    """Handles continuous audio streaming with simultaneous recording and playback"""

    def __init__(
        self,
        client: PhonicAsyncWebsocketClient,
        input_device: int | str | tuple[int, str] | None = None,
        sample_rate: int = 44100,
        chunk_duration_ms: float = 200,
    ):
        try:
            import sounddevice as sd
        except ImportError:
            raise ImportError(
                "The 'sounddevice' library is required to be installed for audio streaming."
            )
        self.sd = sd

        self.client = client
        self.input_device = input_device
        self.sample_rate = sample_rate
        self._chunk_size = int(sample_rate * chunk_duration_ms / 1000)
        self.channels = 1
        self.dtype = np.int16

        self.is_running = False
        self.playback_queue = queue.Queue()

        self.input_stream = None
        self.output_stream = None

        # Event for synchronization
        self.ready_event = asyncio.Event()

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
            self.input_stream.stop()
            self.input_stream.close()

        if self.output_stream:
            self.output_stream.stop()
            self.output_stream.close()

    def _start_input_stream(self):
        """Start audio input stream in a separate thread"""

        def input_callback(indata, frames, time, status):
            if status:
                logger.warning(f"Input stream status: {status}")

            if not self.is_running:
                return

            audio_data = indata.copy().flatten()
            asyncio.run_coroutine_threadsafe(
                self.client.send_audio(audio_data), asyncio.get_event_loop()
            )

        self.input_stream = self.sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            callback=input_callback,
            blocksize=self._chunk_size,
            dtype=self.dtype,
            input_device=self.input_device,
        )
        self.input_stream.start()

    def _start_output_stream(self):
        """Start audio output stream in a separate thread"""

        def output_callback(outdata, frames, time, status):
            if status:
                logger.warning(f"Output stream status: {status}")

            if not self.is_running:
                outdata.fill(0)
                return

            try:
                # Get audio data from queue or fill with zeros if empty
                if not self.playback_queue.empty():
                    audio_chunk = self.playback_queue.get_nowait()
                    if len(audio_chunk) < len(outdata):
                        outdata[: len(audio_chunk)] = audio_chunk.reshape(-1, 1)
                        outdata[len(audio_chunk) :] = 0
                    else:
                        outdata[:] = audio_chunk[: len(outdata)].reshape(-1, 1)
                else:
                    outdata.fill(0)
            except Exception as e:
                logger.error(f"Error in output callback: {e}")
                outdata.fill(0)

        self.output_stream = self.sd.OutputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            callback=output_callback,
            blocksize=self._chunk_size,
            dtype=self.dtype,
        )
        self.output_stream.start()

    def add_audio_to_playback(self, audio_data: np.ndarray):
        """Add audio data to the playback queue"""
        # Process audio in chunks
        for i in range(0, len(audio_data), self._chunk_size):
            end = min(i + self._chunk_size, len(audio_data))
            self.playback_queue.put(audio_data[i:end])
