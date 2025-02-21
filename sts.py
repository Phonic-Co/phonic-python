import asyncio
import base64


from loguru import logger
import numpy as np

from phonic.client import PhonicSTSClient
from phonic.audio_interface import ContinuousAudioInterface


async def main():
    STS_URI = "wss://api.test.phonic.co/v1/sts/ws"
    API_KEY = "FILL THIS IN"
    SAMPLE_RATE = 44100

    try:
        async with PhonicSTSClient(STS_URI, API_KEY) as client:
            audio_streamer = ContinuousAudioInterface(client, sample_rate=SAMPLE_RATE)

            sts_stream = client.sts(
                input_format="pcm_44100",
                output_format="pcm_44100",
                system_prompt="You are a helpful voice assistant. Respond conversationally.",
                # welcome_message="Hello! I'm your voice assistant. How can I help you today?",
                voice_id="katherine",
            )

            await audio_streamer.start()

            logger.info("Starting STS conversation...")
            print("Starting conversation... (Ctrl+C to exit)")
            print("Streaming all audio continuously to the server")

            # Process messages from STS
            async for message in sts_stream:
                message_type = message.get("type")

                if message_type == "audio_chunk":
                    # Decode and queue audio for playback
                    audio_bytes = base64.b64decode(message["audio"])
                    audio_data = np.frombuffer(audio_bytes, dtype=np.int16)
                    audio_streamer.add_audio_to_playback(audio_data)

                elif message_type == "input_text":
                    logger.info(f"You said: {message['text']}")

    except KeyboardInterrupt:
        logger.info("Conversation stopped by user")
        if "audio_streamer" in locals():
            audio_streamer.stop()
    except Exception as e:
        logger.error(f"Error in conversation: {e}")
        if "audio_streamer" in locals():
            audio_streamer.stop()
        raise e


if __name__ == "__main__":
    print("Starting continuous Speech-to-Speech conversation...")
    print("Audio streaming will begin automatically when connected.")
    print("Press Ctrl+C to exit")
    asyncio.run(main())
