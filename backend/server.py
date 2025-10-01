from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timezone
from fuzzywuzzy import fuzz
from geopy.geocoders import Nominatim
import asyncio
import random
from emergentintegrations.llm.chat import LlmChat, UserMessage

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI(title="Trading Address Verification System", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Initialize LLM Chat
llm_chat = LlmChat(
    api_key=os.environ.get('EMERGENT_LLM_KEY'),
    session_id="address-verification",
    system_message="You are an expert address validation assistant. Help verify and normalize addresses by identifying discrepancies, standardizing formats, and providing confidence assessments."
).with_model("openai", "gpt-4o-mini")

# Data Models
class Customer(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    phone: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CustomerCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None

class Address(BaseModel):
    street: str
    city: str
    state: str
    postal_code: str
    country: str

class AddressVerificationRequest(BaseModel):
    customer_id: str
    address: Address
    verification_type: str = "onboarding"  # onboarding, compliance, update

class ValidationSource(BaseModel):
    name: str
    status: str  # success, failed, timeout
    data: Optional[dict] = None
    confidence: float
    response_time_ms: int

class AddressVerification(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str
    original_address: Address
    normalized_address: Optional[Address] = None
    verification_type: str
    overall_confidence: float
    status: str  # verified, suspicious, rejected, pending
    sources: List[ValidationSource]
    ai_assessment: Optional[str] = None
    alerts: List[str] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Mock Data Sources
class MockDataSources:
    @staticmethod
    async def government_registry_api(address: Address) -> ValidationSource:
        """Mock Government Registry API"""
        await asyncio.sleep(random.uniform(0.1, 0.5))  # Simulate API delay
        
        # Mock validation logic - higher confidence for common cities
        common_cities = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Hyderabad", "Pune", "Ahmedabad"]
        confidence = 0.95 if address.city in common_cities else random.uniform(0.6, 0.9)
        
        # Mock normalized data
        normalized_data = {
            "street": address.street.upper(),
            "city": address.city.title(),
            "state": address.state.upper(),
            "postal_code": address.postal_code,
            "country": address.country.upper(),
            "verified": confidence > 0.7
        }
        
        return ValidationSource(
            name="Government Registry API",
            status="success" if confidence > 0.5 else "failed",
            data=normalized_data,
            confidence=confidence,
            response_time_ms=random.randint(100, 500)
        )
    
    @staticmethod
    async def postal_service_api(address: Address) -> ValidationSource:
        """Mock Postal Service API"""
        await asyncio.sleep(random.uniform(0.1, 0.3))
        
        # Check postal code format (basic validation)
        postal_valid = len(address.postal_code) == 6 and address.postal_code.isdigit()
        confidence = 0.9 if postal_valid else 0.3
        
        return ValidationSource(
            name="Postal Service API",
            status="success" if postal_valid else "failed",
            data={"postal_code_valid": postal_valid, "delivery_possible": postal_valid},
            confidence=confidence,
            response_time_ms=random.randint(80, 300)
        )
    
    @staticmethod
    async def maps_geocoding_api(address: Address) -> ValidationSource:
        """Mock Maps Geocoding API using Nominatim (OpenStreetMap)"""
        try:
            geolocator = Nominatim(user_agent="trading-address-verification")
            full_address = f"{address.street}, {address.city}, {address.state}, {address.country}"
            
            # Add timeout to prevent hanging
            location = await asyncio.wait_for(
                asyncio.to_thread(geolocator.geocode, full_address),
                timeout=2.0
            )
            
            if location:
                confidence = 0.85
                data = {
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "formatted_address": location.address,
                    "found": True
                }
                status = "success"
            else:
                confidence = 0.2
                data = {"found": False, "error": "Address not found"}
                status = "failed"
                
        except Exception as e:
            confidence = 0.1
            data = {"found": False, "error": str(e)}
            status = "failed"
        
        return ValidationSource(
            name="Maps Geocoding API",
            status=status,
            data=data,
            confidence=confidence,
            response_time_ms=random.randint(200, 800)
        )

class AddressValidator:
    @staticmethod
    def normalize_address(address: Address) -> Address:
        """Normalize address format"""
        return Address(
            street=address.street.strip().title(),
            city=address.city.strip().title(),
            state=address.state.strip().title(),
            postal_code=address.postal_code.strip(),
            country=address.country.strip().title()
        )
    
    @staticmethod
    def calculate_fuzzy_similarity(addr1: Address, addr2: Address) -> float:
        """Calculate fuzzy similarity between two addresses"""
        street_sim = fuzz.ratio(addr1.street.lower(), addr2.street.lower()) / 100
        city_sim = fuzz.ratio(addr1.city.lower(), addr2.city.lower()) / 100
        state_sim = fuzz.ratio(addr1.state.lower(), addr2.state.lower()) / 100
        postal_sim = fuzz.ratio(addr1.postal_code, addr2.postal_code) / 100
        country_sim = fuzz.ratio(addr1.country.lower(), addr2.country.lower()) / 100
        
        # Weighted average (postal code and city are more important)
        weights = [0.2, 0.3, 0.2, 0.25, 0.05]
        similarities = [street_sim, city_sim, state_sim, postal_sim, country_sim]
        
        return sum(w * s for w, s in zip(weights, similarities))
    
    @staticmethod
    async def get_ai_assessment(address: Address, sources: List[ValidationSource]) -> str:
        """Get AI assessment of address verification"""
        try:
            sources_summary = "\n".join([
                f"- {source.name}: {source.status} (confidence: {source.confidence:.2f})"
                for source in sources
            ])
            
            prompt = f"""Analyze this address verification:

Address: {address.street}, {address.city}, {address.state}, {address.postal_code}, {address.country}

Verification Sources:
{sources_summary}

Provide a brief assessment covering:
1. Overall reliability
2. Key concerns or flags
3. Recommendation (approve/review/reject)

Keep response under 100 words."""

            user_message = UserMessage(text=prompt)
            response = await llm_chat.send_message(user_message)
            return response
        except Exception as e:
            return f"AI assessment unavailable: {str(e)}"
    
    @staticmethod
    def calculate_overall_confidence(sources: List[ValidationSource]) -> tuple[float, str, List[str]]:
        """Calculate overall confidence score and determine status"""
        if not sources:
            return 0.0, "rejected", ["No validation sources available"]
        
        # Weight sources by reliability
        source_weights = {
            "Government Registry API": 0.4,
            "Postal Service API": 0.3,
            "Maps Geocoding API": 0.3
        }
        
        weighted_confidence = 0
        total_weight = 0
        alerts = []
        
        for source in sources:
            weight = source_weights.get(source.name, 0.2)
            if source.status == "success":
                weighted_confidence += source.confidence * weight
                total_weight += weight
            else:
                alerts.append(f"{source.name} verification failed")
        
        overall_confidence = weighted_confidence / total_weight if total_weight > 0 else 0
        
        # Determine status based on confidence
        if overall_confidence >= 0.8:
            status = "verified"
        elif overall_confidence >= 0.6:
            status = "suspicious"
            alerts.append("Moderate confidence - requires review")
        else:
            status = "rejected"
            alerts.append("Low confidence - address verification failed")
        
        return overall_confidence, status, alerts

# API Routes
@api_router.post("/customers", response_model=Customer)
async def create_customer(customer_data: CustomerCreate):
    """Create a new customer"""
    customer = Customer(**customer_data.dict())
    await db.customers.insert_one(customer.dict())
    return customer

@api_router.get("/customers", response_model=List[Customer])
async def get_customers():
    """Get all customers"""
    customers = await db.customers.find().to_list(1000)
    return [Customer(**customer) for customer in customers]

@api_router.get("/customers/{customer_id}", response_model=Customer)
async def get_customer(customer_id: str):
    """Get customer by ID"""
    customer = await db.customers.find_one({"id": customer_id})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return Customer(**customer)

@api_router.post("/verify-address", response_model=AddressVerification)
async def verify_address(request: AddressVerificationRequest):
    """Verify customer address using multiple sources"""
    
    # Check if customer exists
    customer = await db.customers.find_one({"id": request.customer_id})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Normalize the address
    normalized_address = AddressValidator.normalize_address(request.address)
    
    # Run verification from multiple sources concurrently
    verification_tasks = [
        MockDataSources.government_registry_api(request.address),
        MockDataSources.postal_service_api(request.address),
        MockDataSources.maps_geocoding_api(request.address)
    ]
    
    sources = await asyncio.gather(*verification_tasks, return_exceptions=True)
    
    # Filter out exceptions and keep only successful results
    valid_sources = [source for source in sources if isinstance(source, ValidationSource)]
    
    # Calculate overall confidence and status
    overall_confidence, status, alerts = AddressValidator.calculate_overall_confidence(valid_sources)
    
    # Get AI assessment
    ai_assessment = await AddressValidator.get_ai_assessment(request.address, valid_sources)
    
    # Create verification record
    verification = AddressVerification(
        customer_id=request.customer_id,
        original_address=request.address,
        normalized_address=normalized_address,
        verification_type=request.verification_type,
        overall_confidence=overall_confidence,
        status=status,
        sources=valid_sources,
        ai_assessment=ai_assessment,
        alerts=alerts
    )
    
    # Store in database
    await db.address_verifications.insert_one(verification.dict())
    
    return verification

@api_router.get("/verifications", response_model=List[AddressVerification])
async def get_verifications():
    """Get all address verifications"""
    verifications = await db.address_verifications.find().sort("created_at", -1).to_list(1000)
    return [AddressVerification(**verification) for verification in verifications]

@api_router.get("/verifications/{verification_id}", response_model=AddressVerification)
async def get_verification(verification_id: str):
    """Get verification by ID"""
    verification = await db.address_verifications.find_one({"id": verification_id})
    if not verification:
        raise HTTPException(status_code=404, detail="Verification not found")
    return AddressVerification(**verification)

@api_router.get("/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    total_verifications = await db.address_verifications.count_documents({})
    verified_count = await db.address_verifications.count_documents({"status": "verified"})
    suspicious_count = await db.address_verifications.count_documents({"status": "suspicious"})
    rejected_count = await db.address_verifications.count_documents({"status": "rejected"})
    
    # Recent verifications
    recent_verifications = await db.address_verifications.find().sort("created_at", -1).limit(10).to_list(10)
    
    # Average confidence by status
    pipeline = [
        {"$group": {
            "_id": "$status",
            "avg_confidence": {"$avg": "$overall_confidence"},
            "count": {"$sum": 1}
        }}
    ]
    confidence_by_status = await db.address_verifications.aggregate(pipeline).to_list(10)
    
    return {
        "total_verifications": total_verifications,
        "verified_count": verified_count,
        "suspicious_count": suspicious_count,
        "rejected_count": rejected_count,
        "verification_rate": (verified_count / total_verifications * 100) if total_verifications > 0 else 0,
        "recent_verifications": [AddressVerification(**v) for v in recent_verifications],
        "confidence_by_status": confidence_by_status
    }

@api_router.post("/sample-data")
async def load_sample_data():
    """Load sample customer and verification data for demo"""
    
    # Sample customers
    sample_customers = [
        CustomerCreate(name="Rajesh Kumar", email="rajesh.kumar@example.com", phone="+91-9876543210"),
        CustomerCreate(name="Priya Sharma", email="priya.sharma@example.com", phone="+91-9876543211"),
        CustomerCreate(name="Amit Patel", email="amit.patel@example.com", phone="+91-9876543212"),
        CustomerCreate(name="Sneha Gupta", email="sneha.gupta@example.com", phone="+91-9876543213"),
        CustomerCreate(name="Vikram Singh", email="vikram.singh@example.com", phone="+91-9876543214"),
    ]
    
    customers = []
    for customer_data in sample_customers:
        customer = Customer(**customer_data.dict())
        await db.customers.insert_one(customer.dict())
        customers.append(customer)
    
    # Sample addresses for verification
    sample_addresses = [
        Address(street="123 MG Road", city="Mumbai", state="Maharashtra", postal_code="400001", country="India"),
        Address(street="456 Brigade Road", city="Bangalore", state="Karnataka", postal_code="560025", country="India"),
        Address(street="789 Park Street", city="Kolkata", state="West Bengal", postal_code="700016", country="India"),
        Address(street="321 Anna Salai", city="Chennai", state="Tamil Nadu", postal_code="600002", country="India"),
        Address(street="654 Connaught Place", city="Delhi", state="Delhi", postal_code="110001", country="India"),
    ]
    
    # Create verification requests for each customer
    for i, customer in enumerate(customers):
        if i < len(sample_addresses):
            request = AddressVerificationRequest(
                customer_id=customer.id,
                address=sample_addresses[i],
                verification_type="onboarding"
            )
            # Run verification
            await verify_address(request)
    
    return {"message": "Sample data loaded successfully", "customers_created": len(customers)}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()