from enum import Enum
from pydantic import BaseModel, Field

class ActionType(str, Enum):
    OPEN_URL = "OPEN_URL"
    OPEN_PAGE="OPEN_PAGE"
    CLICK="CLICK"
    ENTER_TEXT="ENTER_TEXT"
    SELECT_OPTION="SELECT_OPTION"
    UPLOAD_FILE = "UPLOAD_FILE"
    DOWNLOAD_FILE="DOWNLOAD_FILE"
    READ_TEXT = "READ_TEXT"
    READ_TABLE="READ_TABLE"
    SCROLL="SCROLL"
    WAIT="WAIT"
    SUBMIT="SUBMIT"
    TAKE_SCREENSHOT="TAKE_SCREENSHOT"
    DELETE = "DELETE"
   
    
class WorkflowStep(BaseModel):
    action: ActionType
    target: str
    value: str | None=None
   
    
class Workflow(BaseModel):
    steps: list[WorkflowStep]
   
    
class IntentType(str, Enum):
    ADD_CUSTOMER = "ADD_CUSTOMER"
    ADD_PRODUCT = "ADD_PRODUCT"
    UPDATE_PRODUCT = "UPDATE_PRODUCT"
    DOWNLOAD_REPORT = "DOWNLOAD_REPORT"
    FILL_FORM = "FILL_FORM"
    UPLOAD_FILE = "UPLOAD_FILE"
    READ_TABLE = "READ_TABLE"
    SEND_EMAIL = "SEND_EMAIL"
    DELETE_CUSTOMER = "DELETE_CUSTOMER"
   
    
class Entities(BaseModel):
    data: dict[str, str]={}
    
    
#undersrands what AI understood from the user
class IntentDetectionResponse(BaseModel):
    intent: IntentType
    entities: dict[str, str] = Field(default_factory=dict)
    
    
class ClarificationResponse(BaseModel):
    needs_clarification: bool
    question: str | None=None
    missing_fields: list[str]= Field(default_factory=list)
    
    