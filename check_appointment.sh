#!/bin/bash

# Quick check for new appointments after WhatsApp test

echo "🔍 Checking for new appointments..."
echo ""

# Get appointment count
COUNT=$(mongosh ai_barber_receptionist --quiet --eval "db.appointments.countDocuments({})")
echo "📊 Total appointments: $COUNT"
echo ""

if [ "$COUNT" -gt "0" ]; then
    echo "✅ SUCCESS! Appointments found:"
    echo ""
    mongosh ai_barber_receptionist --quiet --eval "
    db.appointments.find().forEach(function(appt) {
        print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
        print('📅 Appointment ID: ' + appt.appointment_id);
        print('👤 Client: ' + appt.client_name);
        print('📱 Phone: ' + appt.client_phone);
        print('✂️  Service: ' + appt.service);
        print('📆 Date: ' + appt.date);
        print('🕐 Time: ' + appt.time);
        print('📊 Status: ' + appt.status);
        print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
        print('');
    });
    "
    
    echo ""
    echo "🎉 The appointment is now visible on the frontend!"
    echo "   Open: http://localhost:5173"
    echo "   Go to: Appointments page"
    echo ""
else
    echo "❌ No appointments yet."
    echo ""
    echo "Did you send the WhatsApp message?"
    echo "   To: +15556441379"
    echo "   Message: \"I want to book a haircut for tomorrow 2pm. My name is Adel\""
    echo ""
    echo "Check logs for errors:"
    echo "   tail -n 50 /tmp/backend.log | grep -i error"
    echo ""
    echo "Or watch in real-time:"
    echo "   ./watch_logs.sh"
fi
