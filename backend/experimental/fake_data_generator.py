"""
Fake Data Generator for SERA Platform
Generates synthetic events for testing and development.
"""

import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# ─── Constants ──────────────────────────────────────────────────────────────

DOMAINS = ["financial", "healthcare", "iot", "social"]
EVENT_TYPES = ["telemetry", "anomaly_spike", "heartbeat", "auth_attempt", "transaction"]
PROTOCOLS = ["TCP", "HTTP", "HTTPS", "WebSocket", "gRPC"]

FINANCIAL_EVENT_TYPES = ["transaction", "trade", "payment", "settlement", "transfer"]
HEALTHCARE_EVENT_TYPES = ["vital_sign", "medication", "admission", "discharge", "lab_result"]
IOT_EVENT_TYPES = ["sensor_reading", "device_status", "firmware_update", "connection", "alert"]
SOCIAL_EVENT_TYPES = ["post", "like", "share", "comment", "follow"]

# ─── Generator Functions ────────────────────────────────────────────────────

def generate_fake_event(
    entity_id: Optional[str] = None,
    entity_name: Optional[str] = None,
    domain: Optional[str] = None
) -> Dict[str, Any]:
    """Generate a fake event for the stream."""
    if entity_id is None:
        entity_id = f"E-{uuid.uuid4().hex[:8].upper()}"
    if entity_name is None:
        entity_name = f"Entity {random.randint(1, 100)}"
    if domain is None:
        domain = random.choice(DOMAINS)
    
    return {
        "entity_id": entity_id,
        "entity_name": entity_name,
        "domain": domain,
        "event_type": random.choice(EVENT_TYPES),
        "protocol": random.choice(PROTOCOLS),
        "timestamp": datetime.now().isoformat(),
        "entropy": round(random.uniform(0.1, 2.0), 3),
        "alert": random.choice([True, False]),
        "payload": {
            "value": round(random.uniform(0, 100), 2),
            "unit": random.choice(["%", "ms", "count", "bytes"])
        }
    }

def generate_financial_event(
    entity_id: Optional[str] = None,
    entity_name: Optional[str] = None
) -> Dict[str, Any]:
    """Generate a fake financial event."""
    event = generate_fake_event(entity_id, entity_name, "financial")
    event["event_type"] = random.choice(FINANCIAL_EVENT_TYPES)
    event["amount"] = round(random.uniform(100, 100000), 2)
    event["transaction_type"] = random.choice(["buy", "sell", "transfer", "deposit", "withdrawal"])
    event["currency"] = random.choice(["USD", "EUR", "GBP", "JPY", "INR"])
    event["payload"] = {
        "amount": event["amount"],
        "currency": event["currency"],
        "transaction_type": event["transaction_type"]
    }
    return event

def generate_healthcare_event(
    entity_id: Optional[str] = None,
    entity_name: Optional[str] = None
) -> Dict[str, Any]:
    """Generate a fake healthcare event."""
    event = generate_fake_event(entity_id, entity_name, "healthcare")
    event["event_type"] = random.choice(HEALTHCARE_EVENT_TYPES)
    event["vital_sign"] = random.choice(["heart_rate", "blood_pressure", "temperature", "oxygen_saturation"])
    event["value"] = round(random.uniform(60, 140), 1)
    event["unit"] = random.choice(["bpm", "mmHg", "°C", "%"])
    event["payload"] = {
        "vital_sign": event["vital_sign"],
        "value": event["value"],
        "unit": event["unit"]
    }
    return event

def generate_iot_event(
    entity_id: Optional[str] = None,
    entity_name: Optional[str] = None
) -> Dict[str, Any]:
    """Generate a fake IoT event."""
    event = generate_fake_event(entity_id, entity_name, "iot")
    event["event_type"] = random.choice(IOT_EVENT_TYPES)
    event["device_type"] = random.choice(["sensor", "actuator", "gateway", "camera", "thermostat"])
    event["reading"] = round(random.uniform(0, 100), 2)
    event["unit"] = random.choice(["°C", "%", "kPa", "V", "A"])
    event["payload"] = {
        "device_type": event["device_type"],
        "reading": event["reading"],
        "unit": event["unit"],
        "battery_level": random.randint(10, 100)
    }
    return event

def generate_social_event(
    entity_id: Optional[str] = None,
    entity_name: Optional[str] = None
) -> Dict[str, Any]:
    """Generate a fake social event."""
    event = generate_fake_event(entity_id, entity_name, "social")
    event["event_type"] = random.choice(SOCIAL_EVENT_TYPES)
    event["platform"] = random.choice(["twitter", "facebook", "linkedin", "instagram", "reddit"])
    event["engagement"] = random.randint(1, 1000)
    event["sentiment"] = random.choice(["positive", "negative", "neutral"])
    event["payload"] = {
        "platform": event["platform"],
        "engagement": event["engagement"],
        "sentiment": event["sentiment"]
    }
    return event

def generate_random_event(
    entity_id: Optional[str] = None,
    entity_name: Optional[str] = None
) -> Dict[str, Any]:
    """Generate a random event from any domain."""
    generator = random.choice([
        generate_financial_event,
        generate_healthcare_event,
        generate_iot_event,
        generate_social_event
    ])
    return generator(entity_id, entity_name)


class FakeDataGenerator:
    """Class-based fake data generator with state management."""
    
    def __init__(self, seed: Optional[int] = None):
        if seed is not None:
            random.seed(seed)
        self.event_count = 0
        self.generators = [
            generate_financial_event,
            generate_healthcare_event,
            generate_iot_event,
            generate_social_event
        ]
    
    @staticmethod
    def generate_random_event(
        entity_id: Optional[str] = None,
        entity_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a random event."""
        return generate_random_event(entity_id, entity_name)
    
    @staticmethod
    def generate_financial_event(
        entity_id: Optional[str] = None,
        entity_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a financial event."""
        return generate_financial_event(entity_id, entity_name)
    
    @staticmethod
    def generate_healthcare_event(
        entity_id: Optional[str] = None,
        entity_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a healthcare event."""
        return generate_healthcare_event(entity_id, entity_name)
    
    @staticmethod
    def generate_iot_event(
        entity_id: Optional[str] = None,
        entity_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate an IoT event."""
        return generate_iot_event(entity_id, entity_name)
    
    @staticmethod
    def generate_social_event(
        entity_id: Optional[str] = None,
        entity_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a social event."""
        return generate_social_event(entity_id, entity_name)
    
    def generate_batch(self, count: int = 10) -> list:
        """Generate a batch of random events."""
        return [self.generate_random_event() for _ in range(count)]
    
    def generate_events_for_entity(self, entity_id: str, entity_name: str, count: int = 5) -> list:
        """Generate multiple events for a specific entity."""
        events = []
        for _ in range(count):
            generator = random.choice(self.generators)
            events.append(generator(entity_id, entity_name))
        return events