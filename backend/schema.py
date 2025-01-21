from fastapi import Depends, FastAPI, HTTPException, Query
import pandas as pd
import requests
from sqlalchemy import text
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from database import get_db
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from datetime import date, datetime, timedelta
import plotly.graph_objects as go
from fastapi.responses import JSONResponse
import json
import redis


class DataItem(BaseModel):
    t_div: str
    Ship: int
    Customer:str
    AID: str
    Pcs: int
    Weight: int
    Carriers: str
    Pickup: datetime
    Deliv: datetime
    Origin: str
    Origin_State: str
    State1: str
    Zip1: str
    Destination: str
    State2: str
    Destination_State: str
    Zip2: str
    Stage:str

class CountResult(BaseModel):
    Origin_State: str
    State:str
    Zip1: str
    ShipmentCount: int
    lat:float
    lng: Optional[float]
class CountResults(BaseModel):
    Zip2: str
    State2:str
    Destination_State: str
    ShipmentCount: int
    lat: float
    lng: float
       
class Todayshipmets(BaseModel):
    Origin_State: Optional[str]
    OrderCount: int
    
class Lastweekshipments(BaseModel):
    OrderCount: int

class DailyOrderCount(BaseModel):
    OrderDate: date
    OrderCount: int
