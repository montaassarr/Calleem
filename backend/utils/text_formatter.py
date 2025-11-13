"""
Text Formatting Utilities
"""

import re
from typing import Optional
from datetime import datetime


class TextFormatter:
    """
    Utilities for formatting and cleaning text
    """
    
    @staticmethod
    def clean_phone_number(phone: str) -> str:
        """
        Clean and standardize phone number format
        
        Args:
            phone: Raw phone number string
            
        Returns:
            Cleaned phone number with + prefix
        """
        # Remove all non-digit characters
        digits = re.sub(r'\D', '', phone)
        
        # Add country code if not present
        if len(digits) == 10:
            digits = '1' + digits
        
        return '+' + digits
    
    @staticmethod
    def format_phone_display(phone: str) -> str:
        """
        Format phone number for display
        
        Args:
            phone: Phone number string
            
        Returns:
            Formatted phone like (123) 456-7890
        """
        digits = re.sub(r'\D', '', phone)
        
        if len(digits) == 11 and digits[0] == '1':
            digits = digits[1:]
        
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        
        return phone
    
    @staticmethod
    def format_datetime_display(dt: datetime) -> str:
        """
        Format datetime for user-friendly display
        
        Args:
            dt: Datetime object
            
        Returns:
            Formatted string like "Monday, Nov 14 at 3:00 PM"
        """
        return dt.strftime("%A, %b %d at %-I:%M %p")
    
    @staticmethod
    def format_date_display(dt: datetime) -> str:
        """
        Format date for display
        
        Args:
            dt: Datetime object
            
        Returns:
            Formatted string like "Monday, November 14, 2025"
        """
        return dt.strftime("%A, %B %d, %Y")
    
    @staticmethod
    def format_time_display(dt: datetime) -> str:
        """
        Format time for display
        
        Args:
            dt: Datetime object
            
        Returns:
            Formatted string like "3:00 PM"
        """
        return dt.strftime("%-I:%M %p")
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
        """
        Truncate text to maximum length
        
        Args:
            text: Text to truncate
            max_length: Maximum length
            suffix: Suffix to add if truncated
            
        Returns:
            Truncated text
        """
        if len(text) <= max_length:
            return text
        
        return text[:max_length - len(suffix)].rstrip() + suffix
    
    @staticmethod
    def capitalize_name(name: str) -> str:
        """
        Properly capitalize a person's name
        
        Args:
            name: Name string
            
        Returns:
            Capitalized name
        """
        # Split on spaces and capitalize each word
        words = name.strip().split()
        capitalized = []
        
        for word in words:
            # Handle special cases like O'Brien, McDonald
            if "'" in word:
                parts = word.split("'")
                word = "'".join([p.capitalize() for p in parts])
            elif word.lower().startswith("mc") and len(word) > 2:
                word = "Mc" + word[2:].capitalize()
            else:
                word = word.capitalize()
            
            capitalized.append(word)
        
        return " ".join(capitalized)
    
    @staticmethod
    def extract_name_from_text(text: str) -> Optional[str]:
        """
        Try to extract a name from text
        
        Args:
            text: Text containing potential name
            
        Returns:
            Extracted name or None
        """
        # Look for patterns like "I'm John", "My name is John", "This is John"
        patterns = [
            r"(?:i'?m|name'?s|this is)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
            r"([A-Z][a-z]+\s+[A-Z][a-z]+)",  # Two capitalized words
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                name = match.group(1)
                # Validate it's a reasonable name length
                if 2 <= len(name.split()) <= 4:
                    return TextFormatter.capitalize_name(name)
        
        return None
    
    @staticmethod
    def remove_special_chars(text: str, keep_spaces: bool = True) -> str:
        """
        Remove special characters from text
        
        Args:
            text: Text to clean
            keep_spaces: Whether to keep spaces
            
        Returns:
            Cleaned text
        """
        if keep_spaces:
            pattern = r'[^a-zA-Z0-9\s]'
        else:
            pattern = r'[^a-zA-Z0-9]'
        
        return re.sub(pattern, '', text)
    
    @staticmethod
    def format_service_name(service: str) -> str:
        """
        Format service name for display
        
        Args:
            service: Raw service name
            
        Returns:
            Formatted service name
        """
        # Convert to title case and clean up
        service = service.strip().title()
        
        # Fix common abbreviations
        replacements = {
            "And": "and",
            "Or": "or",
            "The": "the"
        }
        
        words = service.split()
        for i, word in enumerate(words):
            if i > 0 and word in replacements:
                words[i] = replacements[word]
        
        return " ".join(words)
    
    @staticmethod
    def pluralize(word: str, count: int) -> str:
        """
        Simple pluralization
        
        Args:
            word: Word to pluralize
            count: Count to determine plural
            
        Returns:
            Singular or plural form
        """
        if count == 1:
            return word
        
        # Simple rules
        if word.endswith('s') or word.endswith('x') or word.endswith('z'):
            return word + 'es'
        elif word.endswith('y') and word[-2] not in 'aeiou':
            return word[:-1] + 'ies'
        else:
            return word + 's'


# Singleton instance
text_formatter = TextFormatter()
