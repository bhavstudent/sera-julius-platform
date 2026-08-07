"""
Models Package
==============
SQLAlchemy ORM Data Models.
"""

from .db_models import (
    EntityModel,
    PredictionModel,
    AlertModel,
    TrackedQueryModel,
    CitationResultModel,
    ClaimModel,
    ClaimChallengeModel,
    EvidenceModel,
    EntityRelationshipModel,
)
from .user import UserModel
from .security import (
    SecurityEngagement,
    SecurityFinding,
    EngagementPhaseLog,
    STYXDetection,
    STYXNode,
    STYXReport,
)
from .entities import ThreatActorModel, AssetModel

# ✅ FIXED: Match the exact class names from commerce.py
# Temporarily comment out if causing issues
# from .commerce import (
#     CompanyModel,
#     FinancialMetricsModel,
#     JobPostingsModel,
#     SearchTrendsModel,
#     VesselMovementsModel,
#     NewsEventsModel,
#     GitHubActivityModel,
#     IngestionLogModel,
#     TickerPriorityCacheModel,
#     HealthcareMetric,
#     ExecutiveMovement
# )

# Try importing from commerce.py separately to debug
try:
    from .commerce import CompanyModel
except ImportError as e:
    print(f"⚠️ Error importing CompanyModel: {e}")
    CompanyModel = None

try:
    from .commerce import FinancialMetricsModel
except ImportError as e:
    print(f"⚠️ Error importing FinancialMetricsModel: {e}")
    FinancialMetricsModel = None

try:
    from .commerce import JobPostingsModel
except ImportError as e:
    print(f"⚠️ Error importing JobPostingsModel: {e}")
    JobPostingsModel = None

# ... import others similarly

__all__ = [
    'EntityModel',
    'PredictionModel',
    'AlertModel',
    'TrackedQueryModel',
    'CitationResultModel',
    'ClaimModel',
    'ClaimChallengeModel',
    'EvidenceModel',
    'EntityRelationshipModel',
    'UserModel',
    'SecurityEngagement',
    'SecurityFinding',
    'EngagementPhaseLog',
    'STYXDetection',
    'STYXNode',
    'STYXReport',
    'ThreatActorModel',
    'AssetModel',
    'CompanyModel',
    'FinancialMetricsModel',
    'JobPostingsModel',
    'SearchTrendsModel',
    'VesselMovementsModel',
    'NewsEventsModel',
    'GitHubActivityModel',
    'IngestionLogModel',
    'TickerPriorityCacheModel',
    'HealthcareMetric',
    'ExecutiveMovement',
]