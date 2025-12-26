from typing import Optional, List, Dict
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON, Text

class CVBase(SQLModel):
    # Base model defining the common attributes of a CV.
    candidate_name: str
    email: Optional[str] = None
    
    # ? Using JSON to store the flexible, semi-structured data extracted by the LLM.
    extracted_data: Dict = Field(default={}, sa_column=Column(JSON))
    
    text_content: Optional[str] = Field(default=None, sa_column=Column(Text))
    
class CV(CVBase, table=True):
    """Database model for the 'CV' table."""
    id: Optional[int] = Field(default=None, primary_key=True)
    is_processed: bool = Field(default=False)
    
class CVCreate(CVBase):
    """Pydantic schema for validating the payload of incoming POST requests (ID is not required)."""
    pass

class Job(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description_text: str = Field(sa_column=Column(Text)) # The content of the Markdown/Txt