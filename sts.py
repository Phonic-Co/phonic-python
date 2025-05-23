import asyncio
import os

from loguru import logger

from phonic.audio_interface import PyaudioContinuousAudioInterface
from phonic.client import PhonicSTSClient, get_voices


async def main():
    STS_URI = "wss://api.phonic.co/v1/sts/ws"
    API_KEY = os.environ["PHONIC_API_KEY"]
    SAMPLE_RATE = 44100

    voices = get_voices(API_KEY)
    voice_ids = [voice["id"] for voice in voices]
    logger.info(f"Available voices: {voice_ids}")
    voice_selected = "greta"

    try:
        async with PhonicSTSClient(STS_URI, API_KEY) as client:
            audio_streamer = PyaudioContinuousAudioInterface(
                client, sample_rate=SAMPLE_RATE
            )

            sts_stream = client.sts(
                input_format="pcm_44100",
                output_format="pcm_44100",
                system_prompt="You are a helpful voice assistant. Respond conversationally.",
                # welcome_message="Hello! I'm your voice assistant. How can I help you today?",
                voice_id=voice_selected,
            )

            await audio_streamer.start()

            logger.info(f"Starting STS conversation with voice {voice_selected}...")
            print("Starting conversation... (Ctrl+C to exit)")
            print("Streaming all audio continuously to the server. Start talking!")

            # Process messages from STS
            text_buffer = ""
            async for message in sts_stream:
                message_type = message.get("type")
                match message_type:
                    case "audio_chunk":
                        audio_streamer.add_audio_to_playback(message["audio"])
                        if text := message.get("text"):
                            text_buffer += text
                            if any(punc in text_buffer for punc in ".!?"):
                                logger.info(f"Assistant: {text_buffer}")
                                text_buffer = ""
                    case "audio_finished":
                        if len(text_buffer) > 0:
                            logger.info(f"Assistant: {text_buffer}")
                            text_buffer = ""
                    case "input_text":
                        logger.info(f"You: {message['text']}")
                    case "interrupted_response":
                        audio_streamer.interrupt_playback()
                        logger.info("Response interrupted")

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
