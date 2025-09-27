#!/usr/bin/env python3
"""
Script to seed appointment slots for testing
"""
from datetime import datetime, timedelta, date, time
from models import get_db, AppointmentSlot
from sqlalchemy.orm import Session
import random

def create_sample_slots():
    """Create sample appointment slots for the next 30 days"""
    db = next(get_db())
    
    # Clear existing slots first
    db.query(AppointmentSlot).delete()
    
    counselors = [
        {"name": "Dr. Sarah Johnson", "email": "sarah.johnson@mindwell.com"},
        {"name": "Dr. Michael Chen", "email": "michael.chen@mindwell.com"},
        {"name": "Dr. Emily Rodriguez", "email": "emily.rodriguez@mindwell.com"}
    ]
    
    # Create slots for the next 30 days
    for day_offset in range(1, 31):  # Start from tomorrow
        current_date = date.today() + timedelta(days=day_offset)
        
        # Skip weekends for now
        if current_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
            continue
            
        # Create time slots for each counselor
        for counselor in counselors:
            # Morning slots (9 AM - 12 PM)
            morning_slots = [
                (time(9, 0), time(9, 50)),
                (time(10, 0), time(10, 50)),
                (time(11, 0), time(11, 50))
            ]
            
            # Afternoon slots (2 PM - 5 PM)
            afternoon_slots = [
                (time(14, 0), time(14, 50)),
                (time(15, 0), time(15, 50)),
                (time(16, 0), time(16, 50))
            ]
            
            all_slots = morning_slots + afternoon_slots
            
            # Randomly make some slots unavailable (simulate bookings)
            for start_time, end_time in all_slots:
                if random.random() < 0.2:  # 20% chance of being unavailable
                    continue
                    
                slot = AppointmentSlot(
                    counselor_name=counselor["name"],
                    counselor_email=counselor["email"],
                    date=current_date,
                    start_time=start_time,
                    end_time=end_time,
                    is_available=True
                )
                db.add(slot)
    
    db.commit()
    print(f"Created appointment slots successfully!")
    
    # Show some stats
    total_slots = db.query(AppointmentSlot).count()
    print(f"Total slots created: {total_slots}")
    
    # Show sample slots
    sample_slots = db.query(AppointmentSlot).limit(5).all()
    print("\nSample slots:")
    for slot in sample_slots:
        print(f"- {slot.counselor_name}: {slot.date} {slot.start_time}-{slot.end_time}")
    
    db.close()

if __name__ == "__main__":
    create_sample_slots()