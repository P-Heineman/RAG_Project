from pydantic import BaseModel, Field
from typing import List, Optional

# ==========================================
# Structured Data Extraction Schemas
# ==========================================

class SourceInfo(BaseModel):
    tool: str = Field(description="שם כלי הקידוד, למשל: cursor, claude_code")
    file: str = Field(description="הנתיב לקובץ ממנו חולץ המידע")

class Decision(BaseModel):
    id: str = Field(description="מזהה ייחודי להחלטה, למשל: dec-001")
    title: str = Field(description="כותרת קצרה של ההחלטה הטכנית")
    summary: str = Field(description="סיכום תמציתי של ההחלטה שהתקבלה")
    tags: List[str] = Field(description="רשימת תגיות, למשל: db, architecture")
    source: SourceInfo
    observed_at: str = Field(description="תאריך ושעה בפורמט ISO 8601")

class Rule(BaseModel):
    id: str = Field(description="מזהה ייחודי לכלל, למשל: rule-001")
    rule: str = Field(description="הגדרת הכלל או ההנחיה")
    scope: str = Field(description="התחום עליו חל הכלל, למשל: ui, backend")
    source: SourceInfo
    observed_at: str = Field(description="תאריך ושעה בפורמט ISO 8601")

class WarningItem(BaseModel):
    id: str = Field(description="מזהה ייחודי לאזהרה, למשל: warn-001")
    area: str = Field(description="האזור או הרכיב הרגיש במערכת")
    message: str = Field(description="תוכן האזהרה או תיאור הרגישות")
    severity: str = Field(description="רמת חומרה, למשל: low, medium, high")
    source: SourceInfo
    observed_at: str = Field(description="תאריך ושעה בפורמט ISO 8601")

class ExtractedItems(BaseModel):
    decisions: List[Decision] = Field(default_factory=list, description="החלטות טכניות")
    rules: List[Rule] = Field(default_factory=list, description="כללים והנחיות")
    warnings: List[WarningItem] = Field(default_factory=list, description="אזהרות ורגישויות")

# ==========================================
# Workflow Parameters Schemas
# ==========================================

class StructuredSearchParams(BaseModel):
    entity_type: str = Field(description="Must be exactly one of: 'decisions', 'rules', 'warnings'")
    keyword: str = Field(default="", description="A word to filter by. If there is no specific keyword, you MUST return an empty string ''.")
    days_back: int = Field(default=0, description="Number of days to look back. If there is no time limit, you MUST return 0.")
