"""Emergency Service logic.

Handles business logic for incidents, resource calculators, and ambulance tracking.
"""
import uuid
from typing import Sequence

from fastapi import HTTPException, status

from app.core.events.bus import event_bus
from app.modules.emergency.models import EmergencyIncident, Ambulance
from app.modules.emergency.repository import EmergencyIncidentRepository, AmbulanceRepository
from app.modules.emergency.schemas import EmergencyIncidentCreate, AmbulanceCreate, ResourceCalculationResponse
from app.modules.emergency.events import EmergencyDeclaredEvent, AmbulanceDispatchedEvent


class EmergencyService:
    """Service layer for emergency response."""
    
    def __init__(self, incident_repo: EmergencyIncidentRepository, ambulance_repo: AmbulanceRepository) -> None:
        self.incident_repo = incident_repo
        self.ambulance_repo = ambulance_repo

    async def get_all_incidents(self, hospital_id: uuid.UUID, skip: int = 0, limit: int = 100) -> Sequence[EmergencyIncident]:
        """Fetch all incidents."""
        return await self.incident_repo.get_all(hospital_id=hospital_id, skip=skip, limit=limit)

    async def create_incident(self, data: EmergencyIncidentCreate, hospital_id: uuid.UUID, actor_id: uuid.UUID) -> EmergencyIncident:
        """Declare a new emergency incident."""
        incident = await self.incident_repo.create(
            title=data.title,
            description=data.description,
            severity=data.severity,
            status=data.status,
            estimated_patients=data.estimated_patients,
            location=data.location,
            hospital_id=hospital_id,
            created_by=actor_id
        )
        
        event = EmergencyDeclaredEvent.create(
            incident_id=incident.id,
            hospital_id=hospital_id,
            actor_id=actor_id,
            severity=incident.severity
        )
        await event_bus.publish(event)
        
        return incident

    async def create_ambulance(self, data: AmbulanceCreate, hospital_id: uuid.UUID, actor_id: uuid.UUID) -> Ambulance:
        """Register or dispatch an ambulance."""
        amb = await self.ambulance_repo.create(
            vehicle_number=data.vehicle_number,
            status=data.status,
            incident_id=data.incident_id,
            gps_location=data.gps_location,
            hospital_id=hospital_id,
            created_by=actor_id
        )
        
        if data.incident_id and data.status == "DISPATCHED":
            event = AmbulanceDispatchedEvent.create(
                ambulance_id=amb.id,
                incident_id=data.incident_id,
                hospital_id=hospital_id,
                actor_id=actor_id
            )
            await event_bus.publish(event)
            
        return amb

    async def calculate_resources(self, incident_id: uuid.UUID) -> ResourceCalculationResponse:
        """Estimate the medical resources required for an active incident."""
        incident = await self.incident_repo.get_by_id(incident_id)
        if not incident:
            raise HTTPException(status_code=404, detail="Incident not found")
            
        # Mock calculation logic
        multiplier = {"LOW": 1, "MEDIUM": 2, "HIGH": 4, "CRITICAL": 10}.get(incident.severity, 1)
        patients = incident.estimated_patients
        
        return ResourceCalculationResponse(
            incident_id=incident.id,
            beds_required=int(patients * 0.8), # 80% might need a bed
            doctors_required=max(1, int(patients / 5)), # 1 doc per 5 patients
            nurses_required=max(1, int(patients / 2)), # 1 nurse per 2 patients
            blood_units_required=int(patients * multiplier * 1.5) # Blood scales heavily with severity
        )
