"""
Tool Schema Generator for N8N Webhook Integration
Generates OpenAI function calling schemas that match N8N webhook expectations
"""

from typing import List, Dict, Any


def generate_tool_schemas(webhook_urls: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    Generate OpenAI function calling schemas for N8N webhooks
    
    Args:
        webhook_urls: Dictionary of webhook URLs (get_slots, book, update, cancel)
        
    Returns:
        List of OpenAI function schemas
    """
    
    schemas = []
    
    # 1. Get Available Slots
    if webhook_urls.get("get_slots"):
        schemas.append({
            "type": "function",
            "function": {
                "name": "get_available_slots",
                "description": "Get available appointment time slots for a specific date. Use this when a customer asks about availability.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "date": {
                            "type": "string",
                            "description": "Date to check availability for, in YYYY-MM-DD format (e.g., '2025-12-01')"
                        }
                    },
                    "required": ["date"]
                },
                "url": webhook_urls["get_slots"]
            }
        })
    
    # 2. Book Appointment
    if webhook_urls.get("book"):
        schemas.append({
            "type": "function",
            "function": {
                "name": "book_appointment",
                "description": "Book a new appointment for a customer. Use this after confirming the customer's preferred time slot.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "email": {
                            "type": "string",
                            "description": "Customer's email address"
                        },
                        "name": {
                            "type": "string",
                            "description": "Customer's full name"
                        },
                        "starttime": {
                            "type": "string",
                            "description": "Appointment start time in ISO 8601 format (e.g., '2025-12-01T10:00:00')"
                        },
                        "notes": {
                            "type": "string",
                            "description": "Additional notes or service requested (e.g., 'Haircut', 'Beard trim')"
                        }
                    },
                    "required": ["email", "name", "starttime"]
                },
                "url": webhook_urls["book"]
            }
        })
    
    # 3. Update Appointment
    if webhook_urls.get("update"):
        schemas.append({
            "type": "function",
            "function": {
                "name": "update_appointment",
                "description": "Reschedule an existing appointment to a new time. Use this when a customer wants to change their appointment time.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "appointment_id": {
                            "type": "string",
                            "description": "ID of the appointment to update"
                        },
                        "email": {
                            "type": "string",
                            "description": "Customer's email address for verification"
                        },
                        "name": {
                            "type": "string",
                            "description": "Customer's name for verification"
                        },
                        "new_time": {
                            "type": "string",
                            "description": "New appointment time in ISO 8601 format (e.g., '2025-12-01T14:00:00')"
                        }
                    },
                    "required": ["appointment_id", "email", "name", "new_time"]
                },
                "url": webhook_urls["update"]
            }
        })
    
    # 4. Cancel Appointment
    if webhook_urls.get("cancel"):
        schemas.append({
            "type": "function",
            "function": {
                "name": "cancel_appointment",
                "description": "Cancel an existing appointment. Use this when a customer wants to cancel their booking.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "appointment_id": {
                            "type": "string",
                            "description": "ID of the appointment to cancel"
                        },
                        "email": {
                            "type": "string",
                            "description": "Customer's email address for verification"
                        },
                        "name": {
                            "type": "string",
                            "description": "Customer's name for verification"
                        }
                    },
                    "required": ["appointment_id", "email", "name"]
                },
                "url": webhook_urls["cancel"]
            }
        })
    
    return schemas


def format_for_vapi(schemas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Format tool schemas for VAPI API
    
    Args:
        schemas: List of OpenAI function schemas
        
    Returns:
        List of VAPI-formatted tool schemas
    """
    vapi_tools = []
    
    for schema in schemas:
        func = schema["function"]
        vapi_tools.append({
            "type": "function",
            "function": {
                "name": func["name"],
                "description": func["description"],
                "parameters": func["parameters"]
            },
            "server": {
                "url": func["url"],
                "timeout_seconds": 20
            },
            "async": False
        })
    
    return vapi_tools
