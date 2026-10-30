from dataclasses import dataclass, asdict
from typing import Optional

@dataclass
class ScholarshipRecord:
    name: str
    provider: str
    official_source_url: str
    application_url: Optional[str] = None
    source_type: str = "Other / unclassified"
    amount: str = "Not specified"
    eligibility: str = "Not specified"
    academic_requirements: str = "Not specified"
    course_level: str = "Not specified"
    income_criteria: str = "Not specified"
    age_criteria: str = "Not specified"
    gender_criteria: str = "Not specified"
    category_criteria: str = "Not specified"
    domicile: str = "Not specified"
    institution_requirements: str = "Not specified"
    opening_date: Optional[str] = None
    closing_date: Optional[str] = None
    documents_required: str = "Not specified"
    selection_process: str = "Not specified"
    renewal_requirements: str = "Not specified"
    current_status: str = "REVIEW_REQUIRED"
    confidence: float = 0.0
    confidence_reason: str = ""
    evidence: list = None

    def to_dict(self):
        d = asdict(self)
        d["evidence"] = self.evidence or []
        return d
