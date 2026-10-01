from pydantic import BaseModel


class SkipSection(BaseModel):
    id: str
    reason: str = ""


class SkipRule(BaseModel):
    id: str
    reason: str = ""
