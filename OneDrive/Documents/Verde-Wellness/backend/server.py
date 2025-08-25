from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from datetime import datetime, timedelta
import uuid
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# MongoDB setup
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "test_database")

client = MongoClient(MONGO_URL)
db = client[DB_NAME]

# Collections
services_collection = db.services
bookings_collection = db.bookings

app = FastAPI(title="Verde Wellness API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class Service(BaseModel):
    id: str
    title: str
    description: str
    price: int
    duration: str
    type: str

class Booking(BaseModel):
    service_id: str
    service_title: str
    date: str
    time: str
    price: int
    status: str = "confirmed"

class BookingResponse(BaseModel):
    id: str
    service_id: str
    service_title: str
    date: str
    time: str
    price: int
    status: str
    created_at: str

# Initialize sample services data
@app.on_event("startup")
async def startup_event():
    # Check if services already exist
    if services_collection.count_documents({}) == 0:
        sample_services = [
            {
                "id": "1",
                "title": "Premium Personal Training",
                "description": "One-on-one sessions with certified trainers, customized workout plans, progress tracking",
                "price": 120,
                "duration": "60 minutes",
                "type": "session"
            },
            {
                "id": "2",
                "title": "Holistic Nutrition Coaching", 
                "description": "Personalized meal plans, grocery guides, weekly check-ins",
                "price": 200,
                "duration": "Monthly",
                "type": "monthly"
            },
            {
                "id": "3",
                "title": "Executive Wellness Package",
                "description": "Combined fitness, nutrition, and mindfulness coaching for busy leaders",
                "price": 450,
                "duration": "Monthly", 
                "type": "monthly"
            }
        ]
        services_collection.insert_many(sample_services)
        print("Sample services inserted into database")

# API Routes
@app.get("/")
async def root():
    return {"message": "Verde Wellness API", "status": "healthy"}

@app.get("/api/services", response_model=List[Service])
async def get_services():
    """Get all available services"""
    try:
        services = list(services_collection.find({}, {"_id": 0}))
        return services
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch services: {str(e)}")

@app.get("/api/availability")
async def get_availability(date: str):
    """Get available time slots for a specific date"""
    try:
        # Parse the date
        booking_date = datetime.fromisoformat(date.replace('Z', '+00:00'))
        date_str = booking_date.strftime("%Y-%m-%d")
        
        # Standard business hours
        all_slots = [
            "09:00", "10:00", "11:00", "14:00", "15:00", "16:00", "17:00"
        ]
        
        # Find existing bookings for this date
        existing_bookings = list(bookings_collection.find({
            "date": {"$regex": f"^{date_str}"}
        }, {"time": 1, "_id": 0}))
        
        booked_times = [booking["time"] for booking in existing_bookings]
        
        # Return available slots (not booked)
        available_slots = [slot for slot in all_slots if slot not in booked_times]
        
        return available_slots
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch availability: {str(e)}")

@app.post("/api/bookings", response_model=BookingResponse)
async def create_booking(booking: Booking):
    """Create a new booking"""
    try:
        # Generate unique booking ID
        booking_id = str(uuid.uuid4())
        
        # Check if time slot is still available
        booking_date = datetime.fromisoformat(booking.date.replace('Z', '+00:00'))
        date_str = booking_date.strftime("%Y-%m-%d")
        
        existing_booking = bookings_collection.find_one({
            "date": {"$regex": f"^{date_str}"},
            "time": booking.time
        })
        
        if existing_booking:
            raise HTTPException(status_code=400, detail="Time slot no longer available")
        
        # Create booking document
        booking_doc = {
            "id": booking_id,
            "service_id": booking.service_id,
            "service_title": booking.service_title,
            "date": booking.date,
            "time": booking.time,
            "price": booking.price,
            "status": booking.status,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Insert into database
        result = bookings_collection.insert_one(booking_doc)
        
        if result.inserted_id:
            return BookingResponse(**booking_doc)
        else:
            raise HTTPException(status_code=500, detail="Failed to create booking")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create booking: {str(e)}")

@app.get("/api/bookings", response_model=List[BookingResponse])
async def get_bookings():
    """Get all bookings"""
    try:
        bookings = list(bookings_collection.find({}, {"_id": 0}))
        return bookings
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch bookings: {str(e)}")

@app.get("/api/bookings/{booking_id}", response_model=BookingResponse)
async def get_booking(booking_id: str):
    """Get a specific booking by ID"""
    try:
        booking = bookings_collection.find_one({"id": booking_id}, {"_id": 0})
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        return BookingResponse(**booking)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch booking: {str(e)}")

@app.delete("/api/bookings/{booking_id}")
async def cancel_booking(booking_id: str):
    """Cancel a booking"""
    try:
        result = bookings_collection.update_one(
            {"id": booking_id},
            {"$set": {"status": "cancelled"}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Booking not found")
            
        return {"message": "Booking cancelled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cancel booking: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)