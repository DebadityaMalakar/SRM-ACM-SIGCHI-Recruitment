from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from datetime import datetime
import json
import os
from typing import List
import logging

logging.basicConfig(level=logging.INFO)

logging.info("Starting the Event Registration API...")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RegistrationRequest(BaseModel):
    name: str
    email: EmailStr

class RegistrationResponse(BaseModel):
    name: str
    email: str
    timestamp: datetime

REGISTRATIONS_FILE = "registrations.json"

def load_registrations() -> List[dict]:
    if not os.path.exists(REGISTRATIONS_FILE):
        return []
    try:
        with open(REGISTRATIONS_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_registrations(registrations: List[dict]):
    with open(REGISTRATIONS_FILE, "w") as f:
        json.dump(registrations, f, indent=2, default=str)

@app.post("/register", response_model=dict)
def register(registration: RegistrationRequest):
    if not registration.name.strip():
        raise HTTPException(status_code=400, detail="Name cannot be empty")
    
    registration_data = {
        "name": registration.name.strip(),
        "email": registration.email,
        "timestamp": datetime.now()
    }
    
    logging.info(registration_data)
    
    registrations = load_registrations()
    registrations.append(registration_data)
    save_registrations(registrations)
    
    return {"message": "Registration successful", "data": registration_data}

@app.get("/registrations", response_model=List[RegistrationResponse])
async def get_registrations():
    registrations = load_registrations()
    return registrations

@app.get("/")
async def root():
    return {"message": "Event Registration API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)