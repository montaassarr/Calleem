# Database Schema Documentation

## Database: MongoDB

Database Name: `ai_barber_receptionist`

---

## Collections

### 1. `appointments`

Stores all client appointments.

**Schema:**
```javascript
{
  _id: ObjectId,                    // Unique appointment ID
  client_name: String,              // Client's full name (required)
  client_phone: String,             // Phone number in E.164 format (required)
  client_email: String,             // Email address (optional)
  service: String,                  // Service name (required)
  datetime: ISODate,                // Appointment date and time (required)
  duration_minutes: Number,         // Duration in minutes (default: 30)
  barber_preference: String,        // Preferred barber name (optional)
  status: String,                   // Enum: pending, confirmed, completed, cancelled, no_show
  conversation_id: String,          // Link to conversation (optional)
  notes: String,                    // Additional notes (optional)
  created_at: ISODate,              // Creation timestamp
  updated_at: ISODate               // Last update timestamp
}
```

**Indexes:**
- `client_phone` (ascending)
- `datetime` (ascending)
- `status` (ascending)
- Compound: `datetime + status` (ascending)

**Example Document:**
```json
{
  "_id": ObjectId("507f1f77bcf86cd799439011"),
  "client_name": "John Doe",
  "client_phone": "+1234567890",
  "client_email": "john@example.com",
  "service": "Haircut",
  "datetime": ISODate("2025-11-15T15:00:00Z"),
  "duration_minutes": 30,
  "barber_preference": "Mike",
  "status": "confirmed",
  "conversation_id": "conv_abc123",
  "notes": "Prefers short fade",
  "created_at": ISODate("2025-11-13T10:00:00Z"),
  "updated_at": ISODate("2025-11-13T10:00:00Z")
}
```

---

### 2. `conversations`

Stores all client-AI conversation transcripts.

**Schema:**
```javascript
{
  _id: ObjectId,                    // Unique document ID
  conversation_id: String,          // Unique conversation identifier
  phone_number: String,             // Client's phone number
  messages: [                       // Array of messages
    {
      role: String,                 // Enum: client, ai, system
      text: String,                 // Message text
      timestamp: ISODate,           // Message timestamp
      metadata: Object              // Additional metadata (optional)
    }
  ],
  state: {                          // Conversation state
    intent: String,                 // Current intent
    collected_info: Object,         // Collected information
    next_question: String,          // Next question to ask
    completed: Boolean              // Whether conversation is complete
  },
  appointment_id: String,           // Linked appointment ID (optional)
  created_at: ISODate,              // Creation timestamp
  updated_at: ISODate               // Last update timestamp
}
```

**Indexes:**
- `phone_number` (ascending)
- `conversation_id` (unique, ascending)
- `created_at` (descending)

**Example Document:**
```json
{
  "_id": ObjectId("507f1f77bcf86cd799439012"),
  "conversation_id": "conv_abc123",
  "phone_number": "+1234567890",
  "messages": [
    {
      "role": "client",
      "text": "Hi, I want a haircut tomorrow at 3pm",
      "timestamp": ISODate("2025-11-13T10:00:00Z"),
      "metadata": {"twilio_message_sid": "SM123456"}
    },
    {
      "role": "ai",
      "text": "Great! What's your name?",
      "timestamp": ISODate("2025-11-13T10:00:05Z"),
      "metadata": null
    },
    {
      "role": "client",
      "text": "John Doe",
      "timestamp": ISODate("2025-11-13T10:00:15Z"),
      "metadata": {"twilio_message_sid": "SM123457"}
    }
  ],
  "state": {
    "intent": "book_appointment",
    "collected_info": {
      "service": "Haircut",
      "date": "tomorrow",
      "time": "3pm",
      "client_name": "John Doe"
    },
    "next_question": null,
    "completed": true
  },
  "appointment_id": "507f1f77bcf86cd799439011",
  "created_at": ISODate("2025-11-13T10:00:00Z"),
  "updated_at": ISODate("2025-11-13T10:01:00Z")
}
```

---

### 3. `services`

Stores available barbershop services.

**Schema:**
```javascript
{
  _id: ObjectId,                    // Unique service ID
  name: String,                     // Service name (unique, required)
  description: String,              // Service description (optional)
  duration_minutes: Number,         // Default duration (required)
  price: Number,                    // Price in dollars (optional)
  active: Boolean,                  // Whether service is active (default: true)
  created_at: ISODate,              // Creation timestamp
  updated_at: ISODate               // Last update timestamp
}
```

**Indexes:**
- `name` (unique, ascending)
- `active` (ascending)

**Example Document:**
```json
{
  "_id": ObjectId("507f1f77bcf86cd799439013"),
  "name": "Haircut",
  "description": "Classic men's haircut with styling",
  "duration_minutes": 30,
  "price": 25.00,
  "active": true,
  "created_at": ISODate("2025-11-01T09:00:00Z"),
  "updated_at": ISODate("2025-11-01T09:00:00Z")
}
```

---

### 4. `users`

Stores admin/staff user accounts.

**Schema:**
```javascript
{
  _id: ObjectId,                    // Unique user ID
  email: String,                    // Email address (unique, required)
  username: String,                 // Username (unique, required)
  full_name: String,                // Full name (required)
  hashed_password: String,          // Bcrypt hashed password
  role: String,                     // Enum: admin, barber, manager
  active: Boolean,                  // Account active status (default: true)
  created_at: ISODate,              // Creation timestamp
  updated_at: ISODate,              // Last update timestamp
  last_login: ISODate               // Last login timestamp (optional)
}
```

**Indexes:**
- `email` (unique, ascending)
- `username` (unique, ascending)

**Example Document:**
```json
{
  "_id": ObjectId("507f1f77bcf86cd799439014"),
  "email": "admin@barbershop.com",
  "username": "admin",
  "full_name": "Admin User",
  "hashed_password": "$2b$12$KIXqZ...",
  "role": "admin",
  "active": true,
  "created_at": ISODate("2025-11-01T09:00:00Z"),
  "updated_at": ISODate("2025-11-13T14:30:00Z"),
  "last_login": ISODate("2025-11-13T14:30:00Z")
}
```

---

## Relationships

```
conversations.appointment_id → appointments._id
conversations.phone_number ← appointments.client_phone
```

---

## Data Types

| Type | Description | Example |
|------|-------------|---------|
| ObjectId | MongoDB unique identifier | `ObjectId("507f1f77bcf86cd799439011")` |
| String | Text data | `"John Doe"` |
| Number | Numeric data | `30`, `25.00` |
| Boolean | True/False | `true` |
| ISODate | Date and time | `ISODate("2025-11-15T15:00:00Z")` |
| Object | Nested document | `{"key": "value"}` |
| Array | List of items | `[item1, item2]` |

---

## Enums

### appointment.status
- `pending` - Appointment requested but not confirmed
- `confirmed` - Appointment confirmed
- `completed` - Service completed
- `cancelled` - Appointment cancelled
- `no_show` - Client didn't show up

### conversation.state.intent
- `greeting` - Initial greeting
- `book_appointment` - Book new appointment
- `update_appointment` - Modify existing appointment
- `cancel_appointment` - Cancel appointment
- `check_availability` - Check time slots
- `service_info` - Ask about services
- `business_info` - Ask about business details
- `general_question` - Other questions
- `unknown` - Intent not determined

### user.role
- `admin` - Full access
- `barber` - Limited access
- `manager` - Management access

### message.role
- `client` - Message from client
- `ai` - Message from AI
- `system` - System message

---

## Queries Examples

### Find upcoming appointments
```javascript
db.appointments.find({
  datetime: { $gte: new Date() },
  status: "confirmed"
}).sort({ datetime: 1 })
```

### Find all conversations for a phone number
```javascript
db.conversations.find({
  phone_number: "+1234567890"
}).sort({ created_at: -1 })
```

### Count appointments by status
```javascript
db.appointments.aggregate([
  { $group: { _id: "$status", count: { $sum: 1 } } }
])
```

### Find active services
```javascript
db.services.find({ active: true })
```

---

## Backup & Restore

### Backup
```bash
mongodump --db=ai_barber_receptionist --out=/backup/
```

### Restore
```bash
mongorestore --db=ai_barber_receptionist /backup/ai_barber_receptionist/
```

---

**Last Updated:** November 13, 2025
