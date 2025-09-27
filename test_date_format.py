#!/usr/bin/env python3
"""
Test script to check the date format returned by the API
"""
import json
from datetime import date
from schemas import AppointmentSlotResponse

# Create a sample slot
sample_slot = {
    "id": 1,
    "counselor_name": "Dr. Test",
    "counselor_email": "test@example.com", 
    "date": date.today(),
    "start_time": "09:00:00",
    "end_time": "09:50:00",
    "is_available": True,
    "created_at": "2024-01-01T09:00:00"
}

# Convert to response model
response = AppointmentSlotResponse(**sample_slot)

# Check JSON format
json_str = response.json()
print("JSON format:")
print(json_str)

# Parse it back
parsed = json.loads(json_str)
print("\nParsed date:")
print(f"Type: {type(parsed['date'])}")
print(f"Value: {parsed['date']}")