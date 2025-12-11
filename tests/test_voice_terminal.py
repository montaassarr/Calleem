#!/usr/bin/env python3
"""
Terminal-based voice conversation with LiveKit AI Agent
This script connects directly to LiveKit and lets you talk to the AI receptionist using your microphone
"""

import asyncio
import json
import sys
import signal
from typing import Optional

try:
    from livekit import rtc, agents
    from livekit.plugins import deepgram, silero
except ImportError:
    print("❌ Missing dependencies. Install with:")
    print("   pip install livekit livekit-agents livekit-plugins-deepgram livekit-plugins-silero")
    sys.exit(1)

try:
    import pyaudio
except ImportError:
    print("❌ Missing pyaudio. Install with:")
    print("   pip install pyaudio")
    print("   On Linux: sudo apt-get install portaudio19-dev python3-pyaudio")
    sys.exit(1)

# Configuration
BACKEND_URL = "http://localhost:8000/api/v1"
USERNAME = "montamsallem@gmail.com"
PASSWORD = "Mariemmontassar03$"

# Audio settings
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000


class VoiceConversation:
    def __init__(self):
        self.room: Optional[rtc.Room] = None
        self.audio_stream: Optional[pyaudio.Stream] = None
        self.token: Optional[str] = None
        self.room_url: Optional[str] = None
        self.room_name: Optional[str] = None
        self.is_running = False
        self.pyaudio_instance = pyaudio.PyAudio()

    async def login(self) -> bool:
        """Login and get JWT token"""
        import httpx
        
        print("🔐 Logging in...")
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{BACKEND_URL}/users/login",
                    data={"username": USERNAME, "password": PASSWORD},
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                
                if response.status_code == 200:
                    self.token = response.json()["access_token"]
                    print("✅ Login successful\n")
                    return True
                else:
                    print(f"❌ Login failed: {response.status_code} - {response.text}")
                    return False
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False

    async def create_session(self) -> bool:
        """Create LiveKit session"""
        import httpx
        
        print("📡 Creating LiveKit session...")
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{BACKEND_URL}/voice-agent/webrtc/test",
                    json={},
                    headers={"Authorization": f"Bearer {self.token}"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.room_name = data["room_name"]
                    self.token = data["token"]
                    self.room_url = data["url"]
                    print(f"✅ Session created")
                    print(f"   Room: {self.room_name}")
                    print(f"   URL: {self.room_url}\n")
                    return True
                else:
                    print(f"❌ Failed to create session: {response.status_code} - {response.text}")
                    return False
        except Exception as e:
            print(f"❌ Session creation error: {e}")
            return False

    async def connect_to_room(self) -> bool:
        """Connect to LiveKit room"""
        print("🔌 Connecting to LiveKit room...")
        
        try:
            self.room = rtc.Room()
            
            # Set up event handlers
            @self.room.on("participant_connected")
            def on_participant_connected(participant: rtc.RemoteParticipant):
                print(f"👤 Participant joined: {participant.identity}")
            
            @self.room.on("track_subscribed")
            def on_track_subscribed(
                track: rtc.Track,
                publication: rtc.RemoteTrackPublication,
                participant: rtc.RemoteParticipant
            ):
                print(f"🎵 Track subscribed: {track.kind} from {participant.identity}")
                if track.kind == rtc.TrackKind.KIND_AUDIO:
                    asyncio.create_task(self.play_audio_track(track))
            
            @self.room.on("data_received")
            def on_data_received(data: rtc.DataPacket):
                try:
                    message = json.loads(data.data.decode())
                    print(f"💬 AI Message: {message}")
                except:
                    pass
            
            # Connect to room
            await self.room.connect(self.room_url, self.token)
            print("✅ Connected to room\n")
            
            # Publish microphone audio
            await self.publish_microphone()
            
            return True
            
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False

    async def publish_microphone(self):
        """Publish microphone audio to the room"""
        print("🎤 Starting microphone...")
        
        try:
            # Create audio source
            source = rtc.AudioSource(RATE, 1)  # 16kHz, mono
            track = rtc.LocalAudioTrack.create_audio_track("microphone", source)
            
            options = rtc.TrackPublishOptions(source=rtc.TrackSource.SOURCE_MICROPHONE)
            publication = await self.room.local_participant.publish_track(track, options)
            
            print("✅ Microphone published\n")
            
            # Start capturing audio
            self.audio_stream = self.pyaudio_instance.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK,
                stream_callback=self.audio_callback_factory(source)
            )
            
            self.audio_stream.start_stream()
            print("🎤 Microphone active - start speaking!\n")
            
        except Exception as e:
            print(f"❌ Microphone error: {e}")

    def audio_callback_factory(self, source: rtc.AudioSource):
        """Create audio callback function"""
        def callback(in_data, frame_count, time_info, status):
            if self.is_running:
                # Convert to audio frame
                frame = rtc.AudioFrame(
                    data=in_data,
                    sample_rate=RATE,
                    num_channels=1,
                    samples_per_channel=frame_count
                )
                source.capture_frame(frame)
            return (None, pyaudio.paContinue)
        return callback

    async def play_audio_track(self, track: rtc.Track):
        """Play audio from the agent"""
        print("🔊 Playing agent audio...")
        
        try:
            # Create audio sink
            sink = rtc.AudioSink(RATE, 1)
            
            # Create PyAudio output stream
            output_stream = self.pyaudio_instance.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                output=True,
                frames_per_buffer=CHUNK
            )
            
            # Set up audio frame handler
            @sink.on("frame_received")
            def on_frame(frame: rtc.AudioFrame):
                if self.is_running:
                    output_stream.write(frame.data.tobytes())
            
            # Subscribe to track
            await track.subscribe()
            track.add_sink(sink)
            
            print("✅ Audio playback active\n")
            
        except Exception as e:
            print(f"❌ Audio playback error: {e}")

    async def run(self):
        """Main conversation loop"""
        if not await self.login():
            return
        
        if not await self.create_session():
            return
        
        if not await self.connect_to_room():
            return
        
        self.is_running = True
        
        print("=" * 60)
        print("🎙️  Voice Agent Active")
        print("=" * 60)
        print("Speak into your microphone to talk to the AI")
        print("Press Ctrl+C to exit\n")
        
        # Keep running until interrupted
        try:
            while self.is_running:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping...")
            self.is_running = False
            
            if self.audio_stream:
                self.audio_stream.stop_stream()
                self.audio_stream.close()
            
            if self.room:
                await self.room.disconnect()
            
            self.pyaudio_instance.terminate()
            print("✅ Disconnected")


async def main():
    conversation = VoiceConversation()
    
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        print("\n🛑 Shutting down...")
        conversation.is_running = False
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    await conversation.run()


if __name__ == "__main__":
    print("=" * 60)
    print("🎤 Terminal Voice Agent Test")
    print("=" * 60)
    print(f"Backend: {BACKEND_URL}")
    print(f"User: {USERNAME}")
    print("=" * 60)
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

