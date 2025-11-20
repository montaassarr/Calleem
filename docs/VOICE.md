## Voice Agent Integration Guide

This project bundles a full-stack voice receptionist that combines Vapi's streaming voice infrastructure with the existing Groq reasoning layer and Mongo persistence. The flow is:

1. Dashboard users trigger outbound tests or start a browser-based WebRTC session.
2. FastAPI calls the Vapi Async API using `VAPI_API_KEY` and injects business metadata (business_id, notes, etc.).
3. Vapi talks to clients, mirrors the WhatsApp receptionist prompt, and emits transcripts.
4. Calls are persisted to the `voice_calls` collection. When enough booking info is present, the Groq agent auto-creates an appointment + WhatsApp confirmation.

The entire feature can be enabled/disabled per tenant by flipping configuration flags—no redeploy required.

---

### Required Environment Variables

| Scope | Variable | Description |
| --- | --- | --- |
| Backend | `VAPI_API_KEY` | Required. Server-side key from Vapi dashboard. |
| Backend | `VAPI_ASSISTANT_ID` | Optional cache. Leave blank to let the service auto-create one. |
| Backend | `VOICE_AGENT_ENABLED` | Global kill-switch. When `true`, bypasses per-business flag checks. |
| Backend | `VOICE_AGENT_TEMPERATURE` | Default Groq temperature for the assistant payload. |
| Backend | `VOICE_AGENT_WEBRTC_PUBLIC_KEY` | Optional placeholder for surfacing the browser key in other services. |
| Backend | `VOICE_AGENT_WEBRTC_ASSISTANT_ID` | Optional static assistant id for WebRTC-only flows. |
| Backend | `ELEVENLABS_API_KEY` | Optional. Required to access ElevenLabs voices. Get from https://elevenlabs.io |
| Backend | `ELEVENLABS_DEFAULT_VOICE` | Default voice ID when ElevenLabs is configured (default: alloy). |
| Backend | `GROQ_API_KEY` | Already required elsewhere; voice reuse the same Groq agent. |
| Frontend | `VITE_API_URL` | Base URL of the FastAPI backend (`http://localhost:8000/api/v1` in dev). |
| Frontend | `VITE_VAPI_PUBLIC_KEY` | Public key from Vapi, required for the in-browser WebRTC console. |
| Frontend | `VITE_VAPI_ASSISTANT_ID` | Optional override that forces the browser client to use a specific assistant. |

> ✅ Tip: Store backend env vars in `.env` next to FastAPI, and frontend vars in `frontend/.env.local` (all must start with `VITE_`).

---

### Enabling Voice Per Business

Voice is off by default for every tenant (`features_enabled.voice_agent = false`). To enable:

```http
PUT /api/v1/business/config
X-Business-ID: default

{
	"features_enabled": {
		"voice_agent": true
	}
}
```

Once enabled, the backend will allow `start-call`, `test-agent`, and `call-history` endpoints for that business. The React dashboard exposes the same toggle inside **Voice Agent → Feature Flag** and automatically persists it via the API above.

Global override: setting `VOICE_AGENT_ENABLED=true` in `.env` skips the business-level check (useful for single-tenant installs). Leave it `false` when you need fine-grained control per customer.

---

### Testing Workflow

1. **Configure secrets**: set all env vars listed above, restart the FastAPI server, and run `npm install && npm run dev` in `frontend/` if you haven't already.
2. **Switch on the feature**: log into the dashboard, open **Voice Agent**, flip the *Voice Agent Access* switch, or call the API manually.
3. **Verify backend connectivity**: click *Run Diagnostics* (or refresh the page) to hit `/voice/test-agent`. You should see the resolved assistant id + Groq model.
4. **Queue an outbound call**: use the *Start Outbound Test Call* form. The backend will sanitize the number, call `AsyncVapi.calls.create`, persist metadata, and, if possible, book an appointment automatically.
5. **Review history**: the *Recent Calls* panel streams documents from MongoDB (`voice_calls` collection). Each entry contains transcript snippets, metadata, and cost information.
6. **WebRTC smoke test** (optional): if `VITE_VAPI_PUBLIC_KEY` is configured, the *WebRTC Test* widget lets you join the assistant directly from the browser using the official `@vapi-ai/web` SDK. Use headphones/mic for best results.

---

### Data Persistence & Automation

| Collection | Purpose |
| --- | --- |
| `voice_calls` | Stores the raw Vapi response (customer, transcript, metadata, cost, assistant id, business_id). |
| `appointments` | When the Groq extraction finds `client_name`, `service`, `date`, and `time`, the service creates a confirmed appointment (`source=voice_agent`) and sends a WhatsApp confirmation via the existing `whatsapp_cloud` service. |

Duplicates are suppressed by matching `client_phone + datetime + service + business_id`.

---

### API Surface

All routes live under `/api/v1/voice` and honor the `X-Business-ID` header.

| Method & Path | Description |
| --- | --- |
| `POST /start-call` | Queues a Vapi call. Body accepts `customer_number`, `customer_name`, and arbitrary `metadata`. |
| `GET /test-agent` | Returns the assistant id + Groq model if the agent is enabled. |
| `GET /call-history?limit=20` | Streams the latest persisted calls for the tenant from Mongo. |

All endpoints require authentication (`get_current_user`).

---

### Troubleshooting

- **"Voice agent disabled" error**: Either the global env flag is off *and* `features_enabled.voice_agent` is false, or Mongo is unavailable. Flip the switch in the dashboard and ensure the DB connection succeeded on startup.
- **WebRTC button disabled**: You must set `VITE_VAPI_PUBLIC_KEY` (and optionally `VITE_VAPI_ASSISTANT_ID`). Restart Vite dev server after editing `.env`.
- **Assistant ID missing**: Delete `VAPI_ASSISTANT_ID` to force recreation, or run `/voice/test-agent` to populate it. Ensure your Vapi API key has permission to create assistants.
- **Appointments not created**: Check `logs/app.log` for `Voice appointment creation failed`. Typically caused by missing required info in the transcript or invalid requested time.
- **Call history empty**: History queries only run when the feature is enabled. Also verify the backend can write to `voice_calls` (look for errors around `_persist_call`).

Need deeper debugging? Watch the FastAPI logs with `tail -f backend/logs/app.log` and enable `DEBUG=True` in `.env` temporarily.
