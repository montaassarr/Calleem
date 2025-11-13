# API Endpoints Documentation

## Base URL
```
Development: http://localhost:8000/api/v1
Production: https://your-domain.com/api/v1
```

---

## 📱 Webhooks

### POST /webhook/sms
Twilio webhook for incoming SMS messages.

**Request (from Twilio):**
```
From: +1234567890
Body: "Hi, I want a haircut"
MessageSid: SM123456...
```

**Response:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>
        Hi there! I'm Ava, the virtual receptionist at Royal Fade. How can I help you today?
    </Message>
</Response>
```

### POST /webhook/voice
Twilio webhook for incoming voice calls.

**Response:** TwiML voice response

---

## 📅 Appointments

### POST /appointments/
Create a new appointment.

**Request Body:**
```json
{
  "client_name": "John Doe",
  "client_phone": "+1234567890",
  "client_email": "john@example.com",
  "service": "Haircut",
  "datetime": "2025-11-15T15:00:00",
  "duration_minutes": 30,
  "barber_preference": "Mike",
  "notes": "Prefers short fade"
}
```

**Response:** `201 Created`
```json
{
  "id": "507f1f77bcf86cd799439011",
  "client_name": "John Doe",
  "client_phone": "+1234567890",
  "client_email": "john@example.com",
  "service": "Haircut",
  "datetime": "2025-11-15T15:00:00",
  "duration_minutes": 30,
  "barber_preference": "Mike",
  "status": "confirmed",
  "conversation_id": null,
  "notes": "Prefers short fade",
  "created_at": "2025-11-13T10:00:00",
  "updated_at": "2025-11-13T10:00:00"
}
```

### GET /appointments/
List all appointments with optional filters.

**Query Parameters:**
- `status` (optional): Filter by status (pending, confirmed, completed, cancelled, no_show)
- `date_from` (optional): ISO datetime
- `date_to` (optional): ISO datetime
- `client_phone` (optional): Filter by phone number
- `skip` (optional): Pagination offset (default: 0)
- `limit` (optional): Max results (default: 100, max: 500)

**Example:**
```bash
GET /appointments/?status=confirmed&date_from=2025-11-15T00:00:00&limit=50
```

**Response:** `200 OK`
```json
[
  {
    "id": "507f1f77bcf86cd799439011",
    "client_name": "John Doe",
    "service": "Haircut",
    "datetime": "2025-11-15T15:00:00",
    "status": "confirmed",
    ...
  }
]
```

### GET /appointments/{appointment_id}
Get a specific appointment.

**Response:** `200 OK`
```json
{
  "id": "507f1f77bcf86cd799439011",
  "client_name": "John Doe",
  ...
}
```

### PUT /appointments/{appointment_id}
Update an appointment.

**Request Body:** (all fields optional)
```json
{
  "datetime": "2025-11-16T14:00:00",
  "status": "completed",
  "notes": "Updated notes"
}
```

**Response:** `200 OK` (updated appointment)

### DELETE /appointments/{appointment_id}
Cancel an appointment (soft delete).

**Response:** `204 No Content`

### GET /appointments/stats/summary
Get appointment statistics.

**Response:** `200 OK`
```json
{
  "total": 150,
  "upcoming": 25,
  "by_status": {
    "confirmed": 20,
    "completed": 100,
    "cancelled": 25,
    "no_show": 5
  }
}
```

---

## 🛠️ Services

### POST /services/
Create a new service.

**Request Body:**
```json
{
  "name": "Haircut",
  "description": "Classic men's haircut with styling",
  "duration_minutes": 30,
  "price": 25.00,
  "active": true
}
```

**Response:** `201 Created`

### GET /services/
List all services.

**Query Parameters:**
- `active_only` (optional): boolean (default: true)
- `skip`, `limit`: pagination

**Response:** `200 OK` (array of services)

### GET /services/{service_id}
Get a specific service.

### PUT /services/{service_id}
Update a service.

### DELETE /services/{service_id}
Deactivate a service (soft delete).

---

## 👤 Users & Authentication

### POST /users/register
Register a new user.

**Request Body:**
```json
{
  "email": "admin@barbershop.com",
  "username": "admin",
  "full_name": "Admin User",
  "password": "SecurePassword123!",
  "role": "admin"
}
```

**Response:** `201 Created`

### POST /users/login
Login and get JWT token.

**Request Body (form data):**
```
username=admin
password=SecurePassword123!
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Usage:**
```bash
# Include token in subsequent requests:
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### GET /users/me
Get current authenticated user.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK` (user object)

### PUT /users/me
Update current user.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:** (all fields optional)
```json
{
  "full_name": "Updated Name",
  "email": "newemail@example.com",
  "password": "NewPassword123!"
}
```

---

## 📊 Response Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Request succeeded |
| 201 | Created - Resource created |
| 204 | No Content - Success, no data to return |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Missing/invalid auth |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 500 | Internal Server Error - Server error |

---

## 🔐 Authentication

Most endpoints require JWT authentication:

1. Login via `/users/login` to get token
2. Include token in `Authorization` header:
   ```
   Authorization: Bearer <your-token>
   ```

**Public Endpoints (no auth required):**
- POST `/users/register`
- POST `/users/login`
- POST `/webhook/sms`
- POST `/webhook/voice`

---

## 🧪 Testing with curl

```bash
# Register user
curl -X POST http://localhost:8000/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","username":"test","full_name":"Test User","password":"Test123!","role":"barber"}'

# Login
curl -X POST http://localhost:8000/api/v1/users/login \
  -d "username=test&password=Test123!"

# Create appointment (with auth token)
curl -X POST http://localhost:8000/api/v1/appointments/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-token>" \
  -d '{"client_name":"John","client_phone":"+1234567890","service":"Haircut","datetime":"2025-11-15T15:00:00","duration_minutes":30}'

# List appointments
curl http://localhost:8000/api/v1/appointments/
```

---

## 🌐 Interactive Documentation

Visit http://localhost:8000/docs for interactive Swagger UI where you can:
- View all endpoints
- Test requests directly
- See request/response schemas
- Authenticate and test protected endpoints

---

**Last Updated:** November 13, 2025
