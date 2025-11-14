# Appointments API - Complete Reference

## Base URL
```
http://localhost:8000/api/v1
```

## Endpoints

### 1. GET /appointments
**List all appointments with optional filters**

**Query Parameters:**
- `status` (optional): Filter by status (confirmed, pending, cancelled, completed)
- `date_from` (optional): Filter appointments from this date (ISO format)
- `date_to` (optional): Filter appointments until this date (ISO format)
- `client_phone` (optional): Filter by client phone number
- `skip` (optional, default: 0): Number of records to skip
- `limit` (optional, default: 100, max: 500): Maximum records to return

**Example:**
```bash
curl http://localhost:8000/api/v1/appointments/
curl "http://localhost:8000/api/v1/appointments/?status=confirmed&date_from=2025-11-15T00:00:00"
```

**Response:** Array of appointment objects

---

### 2. GET /appointments/{appointment_id}
**Get a specific appointment by ID**

**Example:**
```bash
curl http://localhost:8000/api/v1/appointments/69176101b6d07870863c0839
```

**Response:** Single appointment object

---

### 3. POST /appointments
**Create a new appointment**

**Request Body:**
```json
{
  "client_name": "Montassar",
  "client_phone": "+21692034689",
  "client_email": "montassar@example.com",  // optional
  "service": "Haircut",
  "datetime": "2025-11-15T16:00:00",
  "duration_minutes": 30,
  "barber_preference": "John",  // optional
  "notes": "Special instructions"  // optional
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/appointments/ \
  -H "Content-Type: application/json" \
  -d '{
    "client_name": "Montassar",
    "client_phone": "+21692034689",
    "service": "Haircut",
    "datetime": "2025-11-15T16:00:00",
    "duration_minutes": 30
  }'
```

**Response:** Created appointment object

---

### 4. PUT /appointments/{appointment_id}
**Update an existing appointment**

**Request Body:** (all fields optional)
```json
{
  "client_name": "Updated Name",
  "datetime": "2025-11-15T17:00:00",
  "status": "confirmed",
  "notes": "Updated notes"
}
```

**Example:**
```bash
curl -X PUT http://localhost:8000/api/v1/appointments/69176101b6d07870863c0839 \
  -H "Content-Type: application/json" \
  -d '{"datetime": "2025-11-15T17:00:00"}'
```

**Response:** Updated appointment object

---

### 5. DELETE /appointments/{appointment_id}
**Permanently delete an appointment from database**

**Example:**
```bash
curl -X DELETE http://localhost:8000/api/v1/appointments/69176101b6d07870863c0839
```

**Response:** 204 No Content

---

### 6. POST /appointments/{appointment_id}/cancel
**Cancel an appointment (sets status to 'cancelled' but keeps the record)**

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/appointments/69176101b6d07870863c0839/cancel
```

**Response:** Updated appointment object with status='cancelled'

**Note:** This also sends a cancellation SMS to the client.

---

### 7. GET /appointments/availability/check
**Check if a specific time slot is available**

**Query Parameters:**
- `date` (required): Date in YYYY-MM-DD format
- `time` (required): Time in HH:MM format (24-hour)
- `duration_minutes` (optional, default: 30): Duration in minutes

**Example:**
```bash
curl "http://localhost:8000/api/v1/appointments/availability/check?date=2025-11-15&time=15:00&duration_minutes=30"
```

**Response:**
```json
{
  "available": true,
  "requested_datetime": "2025-11-15T15:00:00",
  "duration_minutes": 30,
  "reason": "Time slot is available"
}
```

---

### 8. GET /appointments/stats/summary
**Get appointment statistics**

**Example:**
```bash
curl http://localhost:8000/api/v1/appointments/stats/summary
```

**Response:**
```json
{
  "total": 25,
  "upcoming": 5,
  "by_status": {
    "confirmed": 5,
    "cancelled": 3,
    "completed": 17
  }
}
```

---

## Frontend Usage

### Import the API
```typescript
import { appointmentsApi } from '@/api';
```

### Available Methods

```typescript
// List appointments
const appointments = await appointmentsApi.list();
const filtered = await appointmentsApi.list({ 
  status: 'confirmed', 
  date_from: '2025-11-15T00:00:00' 
});

// Get single appointment
const appointment = await appointmentsApi.get('appointment_id');

// Create appointment
const newAppointment = await appointmentsApi.create({
  client_name: "Montassar",
  client_phone: "+21692034689",
  service: "Haircut",
  datetime: "2025-11-15T16:00:00",
  duration_minutes: 30
});

// Update appointment
const updated = await appointmentsApi.update('appointment_id', {
  datetime: "2025-11-15T17:00:00"
});

// Cancel appointment (keeps record)
const cancelled = await appointmentsApi.cancel('appointment_id');

// Delete appointment (permanent)
await appointmentsApi.delete('appointment_id');

// Check availability
const result = await appointmentsApi.checkAvailability('2025-11-15', '15:00', 30);
console.log(result.available); // true or false

// Get statistics
const stats = await appointmentsApi.getStats();
console.log(stats.total, stats.upcoming);

// Get upcoming appointments
const upcoming = await appointmentsApi.getUpcoming();

// Get appointments by phone
const clientAppts = await appointmentsApi.getByPhone('+21692034689');

// Get appointments by date range
const rangeAppts = await appointmentsApi.getByDateRange(
  '2025-11-15T00:00:00',
  '2025-11-20T23:59:59'
);
```

---

## Testing Page

Visit `/api-test` in the dashboard to test the availability and statistics endpoints with a visual interface.

---

## Response Format

### Appointment Object
```json
{
  "id": "69176101b6d07870863c0839",
  "client_name": "Montassar",
  "client_phone": "+21692034689",
  "client_email": "montassar@example.com",
  "service": "Haircut",
  "datetime": "2025-11-15T16:00:00",
  "duration_minutes": 30,
  "barber_preference": "John",
  "status": "confirmed",
  "conversation_id": "conv_abc123",
  "notes": "Special instructions",
  "created_at": "2025-11-14T17:04:01.459000",
  "updated_at": "2025-11-14T17:04:01.459000"
}
```

### Status Values
- `confirmed`: Appointment is confirmed
- `pending`: Appointment is pending confirmation
- `cancelled`: Appointment was cancelled
- `completed`: Appointment was completed

---

## ngrok Testing

When ngrok is running (`ngrok http 8000`), use the ngrok URL:

```bash
# Get ngrok URL
curl http://localhost:4040/api/tunnels | grep public_url

# Example with ngrok
curl https://nonsustainable-delaine-grabbable.ngrok-free.dev/api/v1/appointments/
```

---

## Webhook Integration

The WhatsApp/SMS webhook at `/api/v1/webhook/sms` will:
1. Create conversations
2. Collect booking information
3. Automatically create appointments when all info is collected
4. Update appointments when user requests time changes
5. Send SMS confirmations via Twilio

All appointments created via WhatsApp will have a `conversation_id` linking to the conversation.
