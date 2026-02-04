from typing import Annotated,Union,List, Optional,Any
import os
from typing_extensions import TypedDict

from pydantic import BaseModel,Field, BeforeValidator, model_validator
import json
from langgraph.graph.message import add_messages

class Filters(BaseModel):
    Match: List['str'] = Field(description='List of table names which need to be queried',default=None)
    Team: List['str'] = Field(description='List of team names whose stats need to be fetched',default=None)
    #Player_Name: List['str'] = Field(description='List of team names whose stats need to be fetched',default=None)
    
class Group(BaseModel):
    fields: List['str'] = Field(description='List of field names which need to be queried from the collection',default=None)
    operator: str = Field(description='Mathematical operator to be applied',default=None)

class State(TypedDict):
    collection: str
    userquery: str
    matches: List[str]|None
    fields: List[str]
    operator: str
    teams: List[str]|None
    #mongoExp: MongoQuery
    response: str
    data: Any
    messages: Annotated[list,add_messages]