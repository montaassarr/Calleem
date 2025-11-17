"""
Dynamic Configuration Loader
Loads business configuration from MongoDB at runtime
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from models.business_config import (
    BusinessConfigInDB, 
    BusinessConfigCreate,
    OpeningHours,
    ServiceDefinition,
    AIConfiguration,
    WhatsAppConfiguration
)
from utils.config import settings

logger = logging.getLogger(__name__)


class ConfigLoader:
    """
    Manages dynamic business configuration from MongoDB
    Falls back to settings.py for initial/default values
    """
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_timestamp: Dict[str, datetime] = {}
        self.cache_ttl_seconds = 300  # 5 minutes
    
    async def get_config(
        self,
        db: AsyncIOMotorDatabase,
        business_id: str = "default"
    ) -> Dict[str, Any]:
        """
        Get business configuration from DB or cache
        
        Args:
            db: MongoDB database instance
            business_id: Business identifier (for multi-tenancy)
            
        Returns:
            Business configuration dictionary
        """
        # Check cache first
        if self._is_cache_valid(business_id):
            logger.debug(f"Using cached config for {business_id}")
            return self._cache[business_id]
        
        # Load from database
        config_doc = await db.business_configs.find_one({"business_id": business_id})
        
        if not config_doc:
            logger.warning(f"No config found for {business_id}, creating default")
            config_doc = await self._create_default_config(db, business_id)
        
        # Update cache
        self._cache[business_id] = config_doc
        self._cache_timestamp[business_id] = datetime.utcnow()
        
        logger.info(f"Loaded config for {business_id}")
        return config_doc
    
    async def update_config(
        self,
        db: AsyncIOMotorDatabase,
        business_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update business configuration
        
        Args:
            db: MongoDB database instance
            business_id: Business identifier
            updates: Fields to update
            
        Returns:
            Updated configuration
        """
        updates["updated_at"] = datetime.utcnow()
        
        result = await db.business_configs.update_one(
            {"business_id": business_id},
            {"$set": updates}
        )
        
        if result.modified_count == 0:
            logger.warning(f"No config updated for {business_id}")
        
        # Invalidate cache
        if business_id in self._cache:
            del self._cache[business_id]
            del self._cache_timestamp[business_id]
        
        # Return updated config
        return await self.get_config(db, business_id)
    
    async def _create_default_config(
        self,
        db: AsyncIOMotorDatabase,
        business_id: str
    ) -> Dict[str, Any]:
        """
        Create default configuration from settings.py
        
        Args:
            db: MongoDB database instance
            business_id: Business identifier
            
        Returns:
            Created configuration document
        """
        # Parse opening hours from settings
        opening_hours = self._parse_opening_hours(settings.BUSINESS_HOURS)
        
        # Parse services from settings
        services = self._parse_services(settings.AVAILABLE_SERVICES)
        
        # Create AI config
        ai_config = AIConfiguration(
            model=settings.GROQ_MODEL,
            system_prompt=self._get_default_system_prompt()
        )
        
        # Create WhatsApp config
        whatsapp_config = WhatsAppConfiguration(
            phone_number_id=settings.WHATSAPP_PHONE_NUMBER_ID,
            access_token=settings.WHATSAPP_TOKEN,
            verify_token=settings.WHATSAPP_VERIFY_TOKEN
        )
        
        config = BusinessConfigCreate(
            business_id=business_id,
            business_name=settings.BUSINESS_NAME,
            business_phone=settings.BUSINESS_PHONE,
            business_email=settings.BUSINESS_EMAIL,
            business_address=settings.BUSINESS_ADDRESS,
            timezone=settings.TIMEZONE,
            opening_hours=opening_hours,
            services=services,
            default_appointment_duration=settings.DEFAULT_APPOINTMENT_DURATION,
            ai_config=ai_config,
            whatsapp_config=whatsapp_config,
            features_enabled={
                "voice_agent": False,
                "email_notifications": False,
                "sms_reminders": False,
                "online_booking": True
            }
        )
        
        config_dict = config.dict()
        config_dict["created_at"] = datetime.utcnow()
        config_dict["updated_at"] = datetime.utcnow()
        
        result = await db.business_configs.insert_one(config_dict)
        config_dict["_id"] = str(result.inserted_id)
        
        logger.info(f"Created default config for {business_id}")
        return config_dict
    
    def _parse_opening_hours(self, hours_string: str) -> list[OpeningHours]:
        """
        Parse opening hours from settings string
        
        Example: "Monday-Saturday 9:00 AM - 8:00 PM"
        """
        # Default hours for common barbershop schedule
        default_hours = [
            OpeningHours(day="monday", open="09:00", close="20:00"),
            OpeningHours(day="tuesday", open="09:00", close="20:00"),
            OpeningHours(day="wednesday", open="09:00", close="20:00"),
            OpeningHours(day="thursday", open="09:00", close="20:00"),
            OpeningHours(day="friday", open="09:00", close="20:00"),
            OpeningHours(day="saturday", open="09:00", close="20:00"),
            OpeningHours(day="sunday", closed=True)
        ]
        
        # TODO: Parse actual hours_string format
        return default_hours
    
    def _parse_services(self, services_string: str) -> list[ServiceDefinition]:
        """
        Parse services from settings string
        
        Example: "Haircut,Beard Trim,Fade,Hot Shave"
        """
        services = []
        for service_name in services_string.split(","):
            service_name = service_name.strip()
            if service_name:
                # Default durations and prices
                duration_map = {
                    "Haircut": 30,
                    "Beard Trim": 15,
                    "Fade": 30,
                    "Hot Shave": 20,
                    "Hair & Beard Combo": 45
                }
                
                services.append(ServiceDefinition(
                    name=service_name,
                    description=f"Professional {service_name.lower()} service",
                    duration_minutes=duration_map.get(service_name, 30),
                    price=0.0,  # Set in UI later
                    active=True
                ))
        
        return services
    
    def _get_default_system_prompt(self) -> str:
        """
        Get the default barber shop AI system prompt
        This will be replaced with the Cyranius-style prompt
        """
        return f"""You are Ava, the friendly virtual receptionist for {settings.BUSINESS_NAME}.

Your role is to help clients:
- Book appointments
- Answer questions about services
- Provide business information
- Reschedule or cancel appointments

Always be warm, professional, and helpful. Keep responses concise and conversational.

Business hours: {settings.BUSINESS_HOURS}
Services: {settings.AVAILABLE_SERVICES}
Phone: {settings.BUSINESS_PHONE}
"""
    
    def _is_cache_valid(self, business_id: str) -> bool:
        """Check if cached config is still valid"""
        if business_id not in self._cache:
            return False
        
        cache_age = (datetime.utcnow() - self._cache_timestamp[business_id]).total_seconds()
        return cache_age < self.cache_ttl_seconds
    
    def invalidate_cache(self, business_id: str = None):
        """Invalidate cache for specific business or all"""
        if business_id:
            if business_id in self._cache:
                del self._cache[business_id]
                del self._cache_timestamp[business_id]
        else:
            self._cache.clear()
            self._cache_timestamp.clear()


# Singleton instance
config_loader = ConfigLoader()
