# n8n Workflow Blueprint for AI Receptionist (Hybrid Architecture)

## Overview
This document describes the updated n8n workflow structure that integrates with the **Core Service API** for multi-tenant support.

## Key Changes from Original
- ❌ **Removed**: Direct Google Calendar API calls
- ❌ **Removed**: Direct Airtable logging
- ✅ **Added**: HTTP requests to Core Service API
- ✅ **Added**: Tenant identification via phone number lookup
- ✅ **Added**: Dynamic API key fetching per tenant

---

## Workflow 1: Get Available Slots

### Webhook Trigger
- **Path**: `/webhook/getslots`
- **Method**: POST
- **Input**: VAPI tool call with `starttime`, `endtime`, `customer.number`

### Flow
1. **Extract Data** (Set Node)
   - `caller_phone`: `{{ $json.body.message.call.customer.number }}`
   - `tool_call_id`: `{{ $json.body.message.toolCalls[0].id }}`
   - `start_time`: `{{ $json.body.message.toolCalls[0].function.arguments.starttime }}`
   - `end_time`: `{{ $json.body.message.toolCalls[0].function.arguments.endtime }}`

2. **Identify Tenant** (HTTP Request)
   - **URL**: `http://core-service:8000/api/v1/tenants/lookup-by-phone`
   - **Method**: POST
   - **Body**: `{ "phone": "{{ $json.caller_phone }}" }`
   - **Output**: `tenant_id`, `tenant_config`

3. **Get Appointments** (HTTP Request)
   - **URL**: `http://core-service:8000/api/v1/appointments`
   - **Method**: GET
   - **Headers**: `X-Tenant-ID: {{ $json.tenant_id }}`
   - **Query**: `?start={{ $json.start_time }}&end={{ $json.end_time }}`
   - **Output**: List of existing appointments

4. **Calculate Available Slots** (Code Node)
   - Use existing logic from original workflow
   - Generate 30-min slots between business hours
   - Exclude booked times

5. **Format Response** (Set Node)
   - `results[0].toolCallId`: `{{ $json.tool_call_id }}`
   - `results[0].result`: `{{ $json.availableTimes }}`

6. **Respond to Webhook**
   - Return formatted response to VAPI

---

## Workflow 2: Book Appointment

### Webhook Trigger
- **Path**: `/webhook/bookslots`
- **Method**: POST
- **Input**: VAPI tool call with `email`, `name`, `notes`, `starttime`, `endtime`

### Flow
1. **Extract Data** (Set Node)
   - Extract all booking parameters

2. **Validate Input** (IF Node)
   - Check if `email`, `name`, `starttime`, `endtime` are provided
   - **False**: Return error response

3. **Identify Tenant** (HTTP Request)
   - Same as Workflow 1

4. **Create Appointment** (HTTP Request)
   - **URL**: `http://core-service:8000/api/v1/appointments`
   - **Method**: POST
   - **Headers**: `X-Tenant-ID: {{ $json.tenant_id }}`
   - **Body**:
     ```json
     {
       "client_name": "{{ $json.name }}",
       "client_email": "{{ $json.email }}",
       "client_phone": "{{ $json.caller_phone }}",
       "datetime": "{{ $json.starttime }}",
       "duration": 30,
       "notes": "{{ $json.notes }}",
       "service_id": "default"
     }
     ```

5. **Handle Success/Error** (IF Node)
   - **Success**: Format success response
   - **Error**: Format error message

6. **Respond to Webhook**

---

## Workflow 3: Update Appointment

### Webhook Trigger
- **Path**: `/webhook/updateslots`
- **Method**: POST

### Flow
1. Extract old and new times
2. Identify tenant
3. **Find Appointment** (HTTP Request)
   - **URL**: `http://core-service:8000/api/v1/appointments/search`
   - **Body**: `{ "phone": "{{ $json.caller_phone }}", "datetime": "{{ $json.old_starttime }}" }`

4. **Update Appointment** (HTTP Request)
   - **URL**: `http://core-service:8000/api/v1/appointments/{{ $json.appointment_id }}`
   - **Method**: PUT
   - **Body**: `{ "datetime": "{{ $json.new_starttime }}" }`

5. Respond to webhook

---

## Workflow 4: Cancel Appointment

### Webhook Trigger
- **Path**: `/webhook/cancelslots`
- **Method**: POST

### Flow
1. Extract cancellation details
2. Identify tenant
3. **Find Appointment** (HTTP Request)
4. **Delete Appointment** (HTTP Request)
   - **URL**: `http://core-service:8000/api/v1/appointments/{{ $json.appointment_id }}`
   - **Method**: DELETE

5. Respond to webhook

---

## Workflow 5: Call Results Logger

### Webhook Trigger
- **Path**: `/webhook/callresults`
- **Method**: POST
- **Input**: VAPI end-of-call report

### Flow
1. **Extract Call Data** (Set Node)
   - `call_id`, `duration`, `cost`, `summary`, `recording_url`

2. **Identify Tenant** (HTTP Request)

3. **Log Conversation** (HTTP Request)
   - **URL**: `http://core-service:8000/api/v1/conversations`
   - **Method**: POST
   - **Headers**: `X-Tenant-ID: {{ $json.tenant_id }}`
   - **Body**:
     ```json
     {
       "phone_number": "{{ $json.caller_phone }}",
       "call_id": "{{ $json.call_id }}",
       "duration": {{ $json.duration }},
       "cost": {{ $json.cost }},
       "summary": "{{ $json.summary }}",
       "recording_url": "{{ $json.recording_url }}"
     }
     ```

4. **Update Tenant Usage** (HTTP Request)
   - **URL**: `http://core-service:8000/api/v1/tenants/{{ $json.tenant_id }}/usage`
   - **Method**: PATCH
   - **Body**: `{ "minutes": {{ $json.duration }}, "calls": 1 }`

---

## Implementation Notes

### Multi-Tenancy
- Every workflow starts by identifying the tenant via phone number lookup
- All Core Service API calls include `X-Tenant-ID` header
- Tenant's API keys are NOT stored in n8n (stored encrypted in Core Service)

### Error Handling
- All HTTP requests should have error branches
- Return user-friendly messages to VAPI

### Environment Variables
- `CORE_SERVICE_URL`: `http://core-service:8000` (or `http://localhost:8000` for local dev)

---

## Next Steps
1. Import this blueprint into n8n UI
2. Create each workflow manually (or use JSON export)
3. Test with VAPI assistant
4. Export final workflows to `workflows/` folder
