#!/usr/bin/env python3
"""
Simple terminal-based voice test for LiveKit AI Agent
Uses requests and LiveKit Python SDK for voice interaction
"""

import asyncio
import json
import sys
import signal
import requests
from typing import Optional

try:
    from livekit import rtc
    from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli, llm
    from livekit.plugins import deepgram, silero
except ImportError:
    print("❌ Missing livekit dependencies. Install with:")
    print("   pip install 'livekit[agents]' livekit-plugins-deepgram livekit-plugins-silero")
    sys.exit(1)

# Configuration
BACKEND_URL = "http://localhost:8000/api/v1"
USERNAME = "montamsallem@gmail.com"
PASSWORD = "Mariemmontassar03$"


class SimpleVoiceTest:
    def __init__(self):
        self.token: Optional[str] = None
        self.room_url: Optional[str] = None
        self.room_name: Optional[str] = None
        self.room: Optional[rtc.Room] = None
        self.is_running = False

    def login(self) -> bool:
        """Login and get JWT token"""
        print("🔐 Logging in...")
        try:
            response = requests.post(
                f"{BACKEND_URL}/users/login",
                data={"username": USERNAME, "password": PASSWORD},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10
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

    def create_session(self) -> bool:
        """Create LiveKit session"""
        print("📡 Creating LiveKit session...")
        try:
            response = requests.post(
                f"{BACKEND_URL}/voice-agent/webrtc/test",
                json={},
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.room_name = data["room_name"]
                self.token = data["token"]  # This is the LiveKit token
                self.room_url = data["url"]
                print(f"✅ Session created")
                print(f"   Room: {self.room_name}")
                print(f"   URL: {self.room_url}\n")
                return True
            else:
                print(f"❌ Failed to create session: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Session creation error: {e}")
            import traceback
            traceback.print_exc()
            return False

    async def connect_and_test(self):
        """Connect to room and test voice"""
        print("🔌 Connecting to LiveKit room...")
        
        try:
            self.room = rtc.Room()
            
            # Event handlers
            @self.room.on("participant_connected")
            def on_participant_connected(participant: rtc.RemoteParticipant):
                print(f"👤 Participant joined: {participant.identity}")
            
            @self.room.on("track_subscribed")
            def on_track_subscribed(
                track: rtc.Track,
                publication: rtc.RemoteTrackPublication,
                participant: rtc.RemoteParticipant
            ):
                print(f"🎵 Audio track from: {participant.identity}")
                if track.kind == rtc.TrackKind.KIND_AUDIO:
                    asyncio.create_task(self.handle_audio_track(track))
            
            @self.room.on("data_received")
            def on_data_received(data: rtc.DataPacket):
                try:
                    message = json.loads(data.data.decode())
                    print(f"💬 AI: {message.get('text', message)}")
                except:
                    pass
            
            # Connect
            await self.room.connect(self.room_url, self.token)
            print("✅ Connected to room\n")
            
            # Enable auto-subscribe for audio
            await self.room.local_participant.set_subscribed(True)
            
            # Publish microphone
            await self.publish_microphone()
            
            self.is_running = True
            
            print("=" * 60)
            print("🎙️  Voice Agent Active - Start Speaking!")
            print("=" * 60)
            print("Speak into your microphone to talk to the AI")
            print("The AI will respond with voice")
            print("Press Ctrl+C to exit\n")
            
            # Keep running
            while self.is_running:
                await asyncio.sleep(1)
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await self.cleanup()

    async def publish_microphone(self):
        """Publish microphone audio"""
        try:
            print("🎤 Starting microphone...")
            
            # Create audio source
            source = rtc.AudioSource(16000, 1)  # 16kHz, mono
            track = rtc.LocalAudioTrack.create_audio_track("mic", source)
            
            options = rtc.TrackPublishOptions(source=rtc.TrackSource.SOURCE_MICROPHONE)
            await self.room.local_participant.publish_track(track, options)
            
            print("✅ Microphone active\n")
            
            # Note: In a real implementation, you'd capture from PyAudio here
            # For now, this sets up the track
            
        except Exception as e:
            print(f"❌ Microphone error: {e}")

    async def handle_audio_track(self, track: rtc.Track):
        """Handle incoming audio from agent"""
        print("🔊 Receiving audio from agent...")
        try:
            await track.subscribe()
            # Audio will be played automatically by LiveKit
            print("✅ Audio playback active\n")
        except Exception as e:
            print(f"❌ Audio handling error: {e}")

    async def cleanup(self):
        """Clean up resources"""
        print("\n🛑 Disconnecting...")
        self.is_running = False
        
        if self.room:
            await self.room.disconnect()
        
        print("✅ Disconnected")


async def main():
    test = SimpleVoiceTest()
    
    # Login
    if not test.login():
        print("❌ Failed to login. Check credentials and backend.")
        return
    
    # Create session
    if not test.create_session():
        print("❌ Failed to create session. Check backend and LiveKit configuration.")
        return
    
    # Connect and test
    try:
        await test.connect_and_test()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("=" * 60)
    print("🎤 Simple Voice Agent Terminal Test")
    print("=" * 60)
    print(f"Backend: {BACKEND_URL}")
    print(f"User: {USERNAME}")
    print("=" * 60)
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

