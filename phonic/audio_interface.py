import asyncio
import base64
import queue
import threading

import numpy as np
from loguru import logger

from phonic.client import PhonicAsyncWebsocketClient


class ContinuousAudioInterface:
    """Handles continuous audio streaming with simultaneous recording and playback"""

    def __init__(
        self,
        client: PhonicAsyncWebsocketClient,
        sample_rate: int = 44100,
    ):
        try:
            import sounddevice as sd
        except ImportError:
            raise ImportError(
                "The 'sounddevice' library is required to be installed for audio streaming."
            )
        self.sd = sd

        self.client = client
        self.sample_rate = sample_rate
        self.channels = 1
        self.dtype = np.int16

        self.is_running = False
        self.playback_queue = queue.Queue()

        self.input_stream = None
        self.output_stream = None

        self.ready_event = asyncio.Event()
        self.main_loop = asyncio.get_event_loop()

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
                self.client.send_audio(audio_data), self.main_loop
            )

        self.input_stream = self.sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            callback=input_callback,
            dtype=self.dtype,
        )
        self.input_stream.start()

    def _start_output_stream(self):
        """Start audio output stream in a separate thread"""

        # Create a persistent buffer to hold leftover audio between callbacks
        self.overflow_buffer = np.array([], dtype=self.dtype)

        def output_callback(outdata, frames, time, status):
            if status:
                logger.warning(f"Output stream status: {status}")

            if not self.is_running:
                outdata.fill(0)
                return

            try:
                # Check if we have enough audio data (either in overflow or queue)
                total_available = len(self.overflow_buffer)
                queue_chunks = []

                # Peek at queue contents without removing them yet
                while not self.playback_queue.empty() and total_available < frames:
                    chunk = self.playback_queue.get_nowait()
                    queue_chunks.append(chunk)
                    total_available += len(chunk)

                # If we don't have enough data, put chunks back and return silence
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
                        # We've filled the output buffer, store remainder in overflow
                        self.overflow_buffer = np.append(self.overflow_buffer, chunk)
                    else:
                        use_frames = min(len(chunk), frames - filled)
                        outdata[filled : filled + use_frames, 0] = chunk[:use_frames]

                        if use_frames < len(chunk):
                            # Store remainder in overflow buffer
                            self.overflow_buffer = np.append(
                                self.overflow_buffer, chunk[use_frames:]
                            )
                        filled += use_frames

            except Exception as e:
                logger.error(f"Error in output callback: {e}")
                outdata.fill(0)

        self.output_stream = self.sd.OutputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            callback=output_callback,
            dtype=self.dtype,
        )
        self.output_stream.start()

    def add_audio_to_playback(self, audio_encoded: str):
        """Add audio data to the playback queue"""
        audio_bytes = base64.b64decode(audio_encoded)
        audio_data = np.frombuffer(audio_bytes, dtype=np.int16)
        self.playback_queue.put(audio_data)
