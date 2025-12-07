from langchain.tools import tool
from typing import Optional, List, Dict
import json
from services.appointments_service import AppointmentsService

class ReceptionistTools:
    
    @tool
    async def check_availability(date: str, time: str, tenant_id: str) -> str:
        """
        Check if a specific date and time is available for booking.
        Args:
            date: Date in YYYY-MM-DD format.
            time: Time in HH:MM format.
            tenant_id: The ID of the business tenant.
        Returns:
            JSON string with availability status.
        """
        result = await AppointmentsService.check_availability(tenant_id, date, time)
        return json.dumps(result)

    @tool
    async def book_appointment(
        customer_name: str,
        customer_email: str,
        date: str,
        time: str,
        tenant_id: str,
        customer_phone: Optional[str] = "",
        service: str = "Appointment"
    ) -> str:
        """
        Book a new appointment.
        Args:
            customer_name: Full name of the customer.
            customer_email: Email address of the customer.
            date: Appointment date YYYY-MM-DD.
            time: Appointment time HH:MM.
            tenant_id: The ID of the business tenant.
            customer_phone: Phone number (optional).
            service: Type of service (default: "Appointment").
        Returns:
            JSON string with booking result.
        """
        result = await AppointmentsService.book_appointment(
            tenant_id=tenant_id,
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            date=date,
            time=time,
            service=service
        )
        return json.dumps(result)

    @tool
    async def list_appointments(customer_email: str, tenant_id: str) -> str:
        """
        List upcoming appointments for a customer by their email address.
        Args:
            customer_email: Email address to search.
            tenant_id: The ID of the business tenant.
        Returns:
            JSON string with list of appointment details.
        """
        result = await AppointmentsService.list_appointments(tenant_id, customer_email)
        return json.dumps(result)

    @tool
    async def cancel_appointment(customer_email: str, date: str, tenant_id: str) -> str:
        """
        Cancel an existing appointment.
        Args:
            customer_email: Email of customer.
            date: Date of appointment to cancel YYYY-MM-DD.
            tenant_id: The ID of the business tenant.
        Returns:
            JSON string with cancellation result.
        """
        result = await AppointmentsService.cancel_appointment_by_email_and_date(
            tenant_id, customer_email, date
        )
        return json.dumps(result)

def get_receptionist_tools():
    return [
        ReceptionistTools.check_availability,
        ReceptionistTools.book_appointment,
        ReceptionistTools.list_appointments,
        ReceptionistTools.cancel_appointment
    ]
