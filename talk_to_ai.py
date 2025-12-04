#!/usr/bin/env python3
"""
Direct terminal-based voice conversation with LiveKit AI Agent
This script connects directly to LiveKit and lets you talk to the AI receptionist
"""
import asyncio
import requests
import json
from livekit import rtc
import pyaudio
import wave
import os
import signal
import sys

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
        self.room = None
        self.audio_source = None
        self.is_speaking = False
        self.token = None
        self.room_url = None
        self.p = pyaudio.PyAudio()
        
    async def login(self):
        """Login and get JWT token"""
        print("🔐 Logging in...")
        response = requests.post(
            f"{BACKEND_URL}/users/login",
            data={"username": USERNAME, "password": PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            print("✅ Login successful\n")
            return True
        else:
            print(f"❌ Login failed: {response.text}")
            return False
    
    async def create_session(self):
        """Create LiveKit session"""
        print("📡 Creating LiveKit session...")
        response = requests.post(
            f"{BACKEND_URL}/voice-agent/webrtc/test",
            json={},
            headers={"Authorization": f"Bearer {self.token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            self.room_name = data["room_name"]
            self.livekit_token = data["token"]
            self.room_url = data["url"]
            print(f"✅ Session created")
            print(f"   Room: {self.room_name}")
            print(f"   URL: {self.room_url}\n")
            return True
        else:
            print(f"❌ Failed to create session: {response.text}")
            return False
    
    async def connect_to_room(self):
        """Connect to LiveKit room"""
        print("🔌 Connecting to LiveKit room...")
        
        self.room = rtc.Room()
        
        # Set up event handlers
        @self.room.on("participant_connected")
        def on_participant_connected(participant: rtc.RemoteParticipant):
            print(f"👤 Participant joined: {participant.identity}")
        
        @self.room.on("track_subscribed")
        def on_track_subscribed(track: rtc.Track, publication: rtc.RemoteTrackPublication, participant: rtc.RemoteParticipant):
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
        try:
            await self.room.connect(self.room_url, self.livekit_token)
            print(f"✅ Connected to room: {self.room.name}")
            print(f"   Local participant: {self.room.local_participant.identity}\n")
            return True
        except Exception as e:
            print(f"❌ Failed to connect: {e}")
            return False
    
    async def play_audio_track(self, track: rtc.AudioTrack):
        """Play incoming audio from AI agent"""
        print("🔊 AI is speaking...")
        self.is_speaking = True
        
        audio_stream = rtc.AudioStream(track)
        
        # Open audio output stream
        stream = self.p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            output=True,
            frames_per_buffer=CHUNK
        )
        
        try:
            async for frame in audio_stream:
                # Convert audio frame to bytes and play
                audio_data = frame.data.tobytes()
                stream.write(audio_data)
        except Exception as e:
            print(f"Error playing audio: {e}")
        finally:
            stream.stop_stream()
            stream.close()
            self.is_speaking = False
            print("🔇 AI finished speaking")
    
    async def start_microphone(self):
        """Capture and stream microphone audio"""
        print("🎤 Starting microphone...")
        
        # Create audio source
        self.audio_source = rtc.AudioSource(RATE, CHANNELS)
        track = rtc.LocalAudioTrack.create_audio_track("microphone", self.audio_source)
        
        # Publish track
        options = rtc.TrackPublishOptions()
        options.source = rtc.TrackSource.SOURCE_MICROPHONE
        
        publication = await self.room.local_participant.publish_track(track, options)
        print(f"✅ Microphone published\n")
        
        # Open audio input stream
        stream = self.p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )
        
        print("=" * 60)
        print("🎙️  READY TO TALK!")
        print("=" * 60)
        print("💡 Start speaking to the AI receptionist")
        print("💡 Try saying: 'I'd like to book an appointment'")
        print("💡 Press Ctrl+C to stop\n")
        
        try:
            while True:
                # Read audio from microphone
                data = stream.read(CHUNK, exception_on_overflow=False)
                
                # Convert to numpy array and push to LiveKit
                import numpy as np
                audio_array = np.frombuffer(data, dtype=np.int16)
                audio_frame = rtc.AudioFrame.create(RATE, CHANNELS, len(audio_array))
                audio_frame.data[:] = audio_array
                
                await self.audio_source.capture_frame(audio_frame)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping conversation...")
        finally:
            stream.stop_stream()
            stream.close()
    
    async def start_conversation(self):
        """Main conversation loop"""
        try:
            if not await self.login():
                return
            
            if not await self.create_session():
                return
            
            if not await self.connect_to_room():
                return
            
            # Wait a moment for agent to join
            print("⏳ Waiting for AI agent to join...")
            await asyncio.sleep(3)
            
            # Start microphone and conversation
            await self.start_microphone()
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await self.cleanup()
    
    async def cleanup(self):
        """Clean up resources"""
        print("\n🧹 Cleaning up...")
        if self.room:
            await self.room.disconnect()
        self.p.terminate()
        print("✅ Disconnected")

def main():
    """Main entry point"""
    print("\n" + "=" * 60)
    print("🤖 AI RECEPTIONIST - TERMINAL VOICE CONVERSATION")
    print("=" * 60)
    print()
    
    conversation = VoiceConversation()
    
    try:
        asyncio.run(conversation.start_conversation())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
