from livekit.plugins import elevenlabs
import inspect

print("ElevenLabs TTS Init Signature:")
print(inspect.signature(elevenlabs.TTS.__init__))
