from fastapi import Depends, FastAPI, HTTPException, Query
import pandas as pd
import requests
from sqlalchemy import text
from pydantic import BaseModel
from typing import List, Optional,Tuple,Dict
from sqlalchemy.orm import Session
from database import get_db
from schema import DataItem,DailyOrderCount,CountResult,CountResults,Todayshipmets,Lastweekshipments
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from datetime import date, datetime, timedelta
import plotly.graph_objects as go
from fastapi.responses import JSONResponse
import json
import redis
from geopy.distance import geodesic


app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Utility for calculating dates
def calculate_date_range(period: str):
    today = datetime.now().date()
    if period == "today":
        first_day = last_day = today
    elif period == "last_month":
        first_day = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
        last_day = today.replace(day=1) - timedelta(days=1)
    elif period == "last_week":
        first_day = today - timedelta(days=today.weekday() + 7)
        last_day = today - timedelta(days=today.weekday() + 1)
    elif period == "this_year":
        first_day = today.replace(month=1, day=1)
        last_day = today.replace(month=12, day=31)
    elif period == "last_year":
        first_day = today.replace(year=today.year - 1, month=1, day=1)
        last_day = today.replace(year=today.year - 1, month=12, day=31)
    else:
        raise ValueError("Invalid period specified.")
    return first_day, last_day

# General database execution function
def execute_query(db: Session, query: str, params: dict, transform_row=None) -> List[dict]:
    sql = text(query)
    try:
        result = db.execute(sql, params)
        if transform_row:
            return [transform_row(row) for row in result]
        else:
            return [{"OrderCount": row.OrderCount} for row in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database query error")

# SQL Queries
DAILY_ORDER_COUNT_QUERY = '''
    SELECT DATE(orders.T_PICKUP) as OrderDate, COUNT(*) as OrderCount
    FROM orders
    LEFT JOIN address origin_address ON origin_address.S_ORDER = orders.T_ORDER AND origin_address.S_TYPE = "O"
    WHERE orders.T_PICKUP BETWEEN :start_date AND :end_date
    GROUP BY OrderDate
    ORDER BY OrderDate
'''

TOTAL_ORDER_COUNT_QUERY = '''
    SELECT COUNT(*) as OrderCount
    FROM orders
    LEFT JOIN address origin_address ON origin_address.S_ORDER = orders.T_ORDER AND origin_address.S_TYPE = "O"
    WHERE orders.T_PICKUP BETWEEN :start_date AND :end_date
'''

# Endpoint examples
# Endpoint for today's orders
@app.get("/origin_shipments_for_Today", response_model=List[Lastweekshipments])
def get_orders_for_today(db: Session = Depends(get_db)):
    start_date, end_date = calculate_date_range("today")
    return execute_query(db, TOTAL_ORDER_COUNT_QUERY, {"start_date": start_date, "end_date": end_date})


@app.get("/origin_shipments_for_LastMonth", response_model=List[Lastweekshipments])
def get_total_orders_for_last_month(db: Session = Depends(get_db)):
    start_date, end_date = calculate_date_range("last_month")
    return execute_query(db, TOTAL_ORDER_COUNT_QUERY, {"start_date": start_date, "end_date": end_date})


@app.get("/origin_shipments_for_LastWeek", response_model=List[Lastweekshipments])
def get_orders_for_last_week(db: Session = Depends(get_db)):
    start_date, end_date = calculate_date_range("last_week")
    return execute_query(db, TOTAL_ORDER_COUNT_QUERY, {"start_date": start_date, "end_date": end_date})


@app.get("/origin_shipments_for_ThisYear", response_model=List[Todayshipmets])
def get_orders_for_this_year(db: Session = Depends(get_db)):
    start_date, end_date = calculate_date_range("this_year")
    query = '''
        SELECT origin_address.S_STATE as State, COUNT(orders.T_ORDER) as OrderCount,
        CONCAT(origin_address.S_CITY, ", ", origin_address.S_STATE) as Origin_State
        FROM orders
        LEFT JOIN address origin_address ON origin_address.S_ORDER = orders.T_ORDER AND origin_address.S_TYPE = "O"
        WHERE orders.T_PICKUP BETWEEN :start_date AND :end_date
        GROUP BY origin_address.S_STATE;
    '''
    return execute_query(db, query, {"start_date": start_date, "end_date": end_date}, 
                         transform_row=lambda row: {"Origin_State": row.Origin_State, "OrderCount": row.OrderCount})


@app.get("/origin_shipments_for_LastYear", response_model=List[Todayshipmets])
def get_orders_for_last_year(db: Session = Depends(get_db)):
    start_date, end_date = calculate_date_range("last_year")
    query = '''
        SELECT origin_address.S_STATE as State, COUNT(orders.T_ORDER) as OrderCount,
        CONCAT(origin_address.S_CITY, ", ", origin_address.S_STATE) as Origin_State
        FROM orders
        LEFT JOIN address origin_address ON origin_address.S_ORDER = orders.T_ORDER AND origin_address.S_TYPE = "O"
        WHERE orders.T_PICKUP BETWEEN :start_date AND :end_date
        GROUP BY origin_address.S_STATE;
    '''
    return execute_query(db, query, {"start_date": start_date, "end_date": end_date}, 
                         transform_row=lambda row: {"Origin_State": row.Origin_State, "OrderCount": row.OrderCount})


@app.get("/origin_shipments_for_Years_barchart", response_model=List[Todayshipmets])
def get_orders_for_lastyear(
    last_day_of_the_year: date,
    first_day_of_the_year: date,
    db: Session = Depends(get_db)
):
    # Convert dates to string in 'YYYY-MM-DD' format
    last_day_of_the_year_str = last_day_of_the_year.strftime('%Y-%m-%d')
    first_day_of_the_year_str = first_day_of_the_year.strftime('%Y-%m-%d')

    query = '''
        SELECT
            origin_address.S_STATE as State,
            COUNT(orders.T_ORDER) as OrderCount,
            CONCAT(origin_address.S_CITY, ", ", origin_address.S_STATE) as Origin_State
        FROM
            orders
        LEFT JOIN
            address origin_address ON origin_address.S_ORDER = orders.T_ORDER AND origin_address.S_TYPE = "O"
        WHERE orders.T_PICKUP BETWEEN :first_day_of_the_year AND :last_day_of_the_year
        GROUP BY
            origin_address.S_STATE;
    '''

    sql = text(query)

    try:
        result = db.execute(sql, {"first_day_of_the_year": first_day_of_the_year_str, "last_day_of_the_year": last_day_of_the_year_str})
        get_data = []

        for row in result:
            item = {
                "Origin_State": row.Origin_State,       
                "OrderCount": row.OrderCount,  
            }
            get_data.append(item)

        return get_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/origin_shipments_for_TwoMonthsAgo", response_model=List[DailyOrderCount])
def get_orders_for_two_months_ago(db: Session = Depends(get_db)):
    today = datetime.now().date()
    first_day_of_two_months_ago = (today.replace(day=1) - timedelta(days=1)).replace(day=1) - timedelta(days=1)
    first_day_of_two_months_ago = first_day_of_two_months_ago.replace(day=1)
    last_day_of_two_months_ago = (first_day_of_two_months_ago.replace(day=1) + timedelta(days=31)).replace(day=1) - timedelta(days=1)
    
    query = DAILY_ORDER_COUNT_QUERY
    return execute_query(db, query, {"start_date": first_day_of_two_months_ago, "end_date": last_day_of_two_months_ago},
                         transform_row=lambda row: {"OrderDate": row.OrderDate, "OrderCount": row.OrderCount})

@app.get("/origin_shipments_for_LastMonth_Per_Day", response_model=List[DailyOrderCount])
def get_orders_for_lastmonth_per_day(db: Session = Depends(get_db)):
    today = datetime.now().date()
    first_day_of_current_month = today.replace(day=1)
    last_day_of_last_month = first_day_of_current_month - timedelta(days=1)
    first_day_of_last_month = last_day_of_last_month.replace(day=1)
    
    query = DAILY_ORDER_COUNT_QUERY
    return execute_query(db, query, {"start_date": first_day_of_last_month, "end_date": last_day_of_last_month},
                         transform_row=lambda row: {"OrderDate": row.OrderDate, "OrderCount": row.OrderCount})
    
# Function to execute SQL query
def execute_query_per_day(db: Session, query: str, params: dict):
    # Execute the query and return the result in the expected format
    query = text(query)
    result = db.execute(query, params).fetchall()
    return [
        {
            "State": row[0],        
            "OrderCount": row[1],   
            "Origin_State": row[2]  
        }
            for row in result
    ]


@app.get("/originshipmentsfortoday", response_model=List[Todayshipmets])
def get_orders_for_today(today: date, db: Session = Depends(get_db)):
    # SQL query for today shipments
    TODAY_SHIPMENTS_QUERY = '''
        SELECT
            origin_address.S_STATE as State,
            COUNT(orders.T_ORDER) as OrderCount,
            CONCAT(origin_address.S_CITY, ", ", origin_address.S_STATE) as Origin_State
        FROM
            orders
        LEFT JOIN
            address origin_address ON origin_address.S_ORDER = orders.T_ORDER AND origin_address.S_TYPE = "O"
        WHERE
            orders.T_PICKUP = :today
        GROUP BY
            origin_address.S_STATE;
    '''
    return execute_query_per_day(db, TODAY_SHIPMENTS_QUERY, {"today": today})


def get_first_and_last_of_last_year():
    today = date.today()
    first_day_last_year = date(today.year - 1, 1, 1)  
    last_day_last_year = date(today.year - 1, 12, 31) 
    return first_day_last_year, last_day_last_year

@app.get("/countoriginshipmentsHome", response_model=List[CountResult])
def get_zipcodes_with_most_originshipmentHome(
    start_date: date = Depends(lambda: get_first_and_last_of_last_year()[0]),  # Default to first day of last year
    end_date: date = Depends(lambda: get_first_and_last_of_last_year()[1]),    # Default to last day of last year
    db: Session = Depends(get_db)
):
    query = '''
        SELECT 
            orders.t_div, orders.T_ORDER as Ship, orders.T_AID as Customer, orders.T_AID as AID, 
            orders.T_PIECES as Pcs, orders.T_AWEIGHT as Weight, orders_reg_info.CARRIER as Carriers,
            orders.T_PICKUP as Pickup, orders.T_DELIV as Deliv, origin_address.S_CITY as Origin,  
            origin_address.S_STATE as State1, CONCAT(origin_address.S_CITY, ", ", origin_address.S_STATE) as Origin_State, 
            origin_address.S_ZIP as Zip1, dest_address.S_CITY as Destination,
            dest_address.S_STATE as State2, dest_address.S_ZIP as Zip2, 
            CONCAT(dest_address.S_CITY, ", ", dest_address.S_STATE) as Destination_State, orders.stage as Stage,
            COUNT(*) as ShipmentCount 
        FROM orders 
        LEFT JOIN address origin_address ON origin_address.S_ORDER = orders.T_ORDER AND origin_address.S_TYPE="O" 
        LEFT JOIN address dest_address ON dest_address.S_ORDER = orders.T_ORDER AND dest_address.S_TYPE="D"
        LEFT JOIN orders_reg_info ON orders_reg_info.R_ORDER = orders.T_ORDER 
        WHERE orders.T_PICKUP BETWEEN :start_date AND :end_date
        GROUP BY origin_address.S_STATE
        ORDER BY ShipmentCount DESC;
    '''

    sql = text(query)
    params = {
        "start_date": start_date,
        "end_date": end_date,
    }

    result = db.execute(sql, params)
    get_data = []
    cities_data = pd.DataFrame(pd.read_csv('uscitiesdataset/uscities_updated.csv'))

    for row in result:
        item = {
            "Zip1": row.Zip1,
            "State": row.State1,
            "Origin_State": row.Origin_State,
            "ShipmentCount": row.ShipmentCount,
            "lat": 0.0,
            "lng": 0,
        }
        
        if any(cities_data['city_state'].str.contains(row.Origin_State)):
            zip_info = cities_data[cities_data['city_state'].str.contains(row.Origin_State)]
            item["lat"] = float(zip_info.iloc[0]['lat'])
            item["lng"] = float(zip_info.iloc[0]['lng'])
        
        get_data.append(item)

    return get_data

@app.get("/countdestinationshipmentsHome", response_model=List[CountResults])
def get_zipcodes_with_most_destinationshipmentHome(
    start_date: date = Depends(lambda: get_first_and_last_of_last_year()[0]),  # Default to first day of last year
    end_date: date = Depends(lambda: get_first_and_last_of_last_year()[1]),    # Default to last day of last year
    db: Session = Depends(get_db)
):
    query = '''
        SELECT 
            orders.t_div, orders.T_ORDER as Ship, orders.T_AID as Customer, orders.T_AID as AID, 
            orders.T_PIECES as Pcs, orders.T_AWEIGHT as Weight, orders_reg_info.CARRIER as Carriers,
            orders.T_PICKUP as Pickup, orders.T_DELIV as Deliv, origin_address.S_CITY as Origin,  
            origin_address.S_STATE as State1, CONCAT(origin_address.S_CITY, ", ", origin_address.S_STATE) as Origin_State, 
            origin_address.S_ZIP as Zip1, dest_address.S_CITY as Destination,
            dest_address.S_STATE as State2, dest_address.S_ZIP as Zip2, 
            CONCAT(dest_address.S_CITY, ", ", dest_address.S_STATE) as Destination_State, orders.stage as Stage,
            COUNT(*) as ShipmentCount 
        FROM orders 
        LEFT JOIN address origin_address ON origin_address.S_ORDER = orders.T_ORDER AND origin_address.S_TYPE="O" 
        LEFT JOIN address dest_address ON dest_address.S_ORDER = orders.T_ORDER AND dest_address.S_TYPE="D"
        LEFT JOIN orders_reg_info ON orders_reg_info.R_ORDER = orders.T_ORDER 
        WHERE orders.T_PICKUP BETWEEN :start_date AND :end_date
        GROUP BY dest_address.S_STATE
        ORDER BY ShipmentCount DESC;
    '''

    sql = text(query)
    params = {
        "start_date": start_date,
        "end_date": end_date,
    }


    result = db.execute(sql, params)
    get_data = []
    cities_data = pd.DataFrame(pd.read_csv('uscitiesdataset/uscities_updated.csv'))
    
    for row in result:
        item = {
            "Zip2": row.Zip2,
            "State2": row.State2,
            "Destination_State": row.Destination_State,
            "ShipmentCount": row.ShipmentCount,
            "Stage": row.Stage,
            "lat": 0.0,
            "lng": 0.0,
        }

        if any(cities_data['city_state'].str.contains(row.Destination_State)):
            zip_info = cities_data[cities_data['city_state'].str.contains(row.Destination_State)]
            item["lat"] = float(zip_info.iloc[0]['lat'])
            item["lng"] = float(zip_info.iloc[0]['lng'])

        get_data.append(item)

    return get_data

def get_first_and_last_of_last_year() -> Tuple[date, date]:
    today = date.today()
    return date(today.year - 1, 1, 1), date(today.year - 1, 12, 31)
# shipments for the map in home 
def get_shipment_data(
    query: str,
    params: dict,
    db: Session,
    cities_data: pd.DataFrame,
    state_field: str,
    zipcode_field: str,
    state_name_field: str
) -> List[dict]:
    result = db.execute(text(query), params)
    data = []

    for row in result:
        item = {
            zipcode_field: getattr(row, zipcode_field),
            state_field: getattr(row, state_field),
            state_name_field: getattr(row, state_name_field),
            "ShipmentCount": row.ShipmentCount,
            "lat": 0.0,
            "lng": 0.0,
        }
        
        if any(cities_data['city_state'].str.contains(getattr(row, state_name_field))):
            zip_info = cities_data[cities_data['city_state'].str.contains(getattr(row, state_name_field))]
            item["lat"] = float(zip_info.iloc[0]['lat'])
            item["lng"] = float(zip_info.iloc[0]['lng'])
        
        data.append(item)
    
    return data

# @app.get("/countoriginshipmentsHome", response_model=List[CountResult])
# def get_zipcodes_with_most_originshipmentHome(
#     start_date: date = Depends(lambda: get_first_and_last_of_last_year()[0]),
#     end_date: date = Depends(lambda: get_first_and_last_of_last_year()[1]),
#     db: Session = Depends(get_db)
# ):
#     query = '''
#         SELECT 
#             orders.t_div, orders.T_ORDER as Ship, orders.T_AID as Customer, orders.T_AID as AID, 
#             orders.T_PIECES as Pcs, orders.T_AWEIGHT as Weight, orders_reg_info.CARRIER as Carriers,
#             orders.T_PICKUP as Pickup, orders.T_DELIV as Deliv, origin_address.S_CITY as Origin,  
#             origin_address.S_STATE as State1, CONCAT(origin_address.S_CITY, ", ", origin_address.S_STATE) as Origin_State, 
#             origin_address.S_ZIP as Zip1, dest_address.S_CITY as Destination,
#             dest_address.S_STATE as State2, dest_address.S_ZIP as Zip2, 
#             CONCAT(dest_address.S_CITY, ", ", dest_address.S_STATE) as Destination_State, orders.stage as Stage,
#             COUNT(*) as ShipmentCount 
#         FROM orders 
#         LEFT JOIN address origin_address ON origin_address.S_ORDER = orders.T_ORDER AND origin_address.S_TYPE="O" 
#         LEFT JOIN address dest_address ON dest_address.S_ORDER = orders.T_ORDER AND dest_address.S_TYPE="D"
#         LEFT JOIN orders_reg_info ON orders_reg_info.R_ORDER = orders.T_ORDER 
#         WHERE orders.T_PICKUP BETWEEN :start_date AND :end_date
#         GROUP BY origin_address.S_STATE
#         ORDER BY ShipmentCount DESC;
#     '''
#     cities_data = pd.DataFrame(pd.read_csv('uscitiesdataset/uscities_updated.csv'))
#     params = {"start_date": start_date, "end_date": end_date}
    
#     return get_shipment_data(query, params, db, cities_data, "State1", "Zip1", "Origin_State")

# @app.get("/countdestinationshipmentsHome", response_model=List[CountResults])
# def get_zipcodes_with_most_destinationshipmentHome(
#     start_date: date = Depends(lambda: get_first_and_last_of_last_year()[0]),
#     end_date: date = Depends(lambda: get_first_and_last_of_last_year()[1]),
#     db: Session = Depends(get_db)
# ):
#     query = '''
#         SELECT 
#             orders.t_div, orders.T_ORDER as Ship, orders.T_AID as Customer, orders.T_AID as AID, 
#             orders.T_PIECES as Pcs, orders.T_AWEIGHT as Weight, orders_reg_info.CARRIER as Carriers,
#             orders.T_PICKUP as Pickup, orders.T_DELIV as Deliv, origin_address.S_CITY as Origin,  
#             origin_address.S_STATE as State1, CONCAT(origin_address.S_CITY, ", ", origin_address.S_STATE) as Origin_State, 
#             origin_address.S_ZIP as Zip1, dest_address.S_CITY as Destination,
#             dest_address.S_STATE as State2, dest_address.S_ZIP as Zip2, 
#             CONCAT(dest_address.S_CITY, ", ", dest_address.S_STATE) as Destination_State, orders.stage as Stage,
#             COUNT(*) as ShipmentCount 
#         FROM orders 
#         LEFT JOIN address origin_address ON origin_address.S_ORDER = orders.T_ORDER AND origin_address.S_TYPE="O" 
#         LEFT JOIN address dest_address ON dest_address.S_ORDER = orders.T_ORDER AND dest_address.S_TYPE="D"
#         LEFT JOIN orders_reg_info ON orders_reg_info.R_ORDER = orders.T_ORDER 
#         WHERE orders.T_PICKUP BETWEEN :start_date AND :end_date
#         GROUP BY dest_address.S_STATE
#         ORDER BY ShipmentCount DESC;
#     '''
#     cities_data = pd.DataFrame(pd.read_csv('uscitiesdataset/uscities_updated.csv'))
#     params = {"start_date": start_date, "end_date": end_date}

#     return get_shipment_data(query, params, db, cities_data, "State2", "Zip2", "Destination_State")

@app.get("/countoriginshipments", response_model=List[CountResult])
def get_zipcodes_with_most_originshipment(
    start_date: date,
    end_date: date,
    from_weights_value: Optional[int] = None,
    to_weights_value: Optional[int] = None,
    zip_code: Optional[str] = None,
    shipment_value: Optional[str] = Query(None),
    stage: Optional[List[str]] = Query(None),
    db: Session = Depends(get_db)
):
    query = '''
        SELECT 
            orders.t_div, orders.T_ORDER as Ship, orders.T_AID as Customer, orders.T_AID as AID, 
            orders.T_PIECES as Pcs, orders.T_AWEIGHT as Weight, orders_reg_info.CARRIER as Carriers,
            orders.T_PICKUP as Pickup, orders.T_DELIV as Deliv, origin_address.S_CITY as Origin,  
            origin_address.S_STATE as State1, CONCAT(origin_address.S_CITY, ", ", origin_address.S_STATE) as Origin_State, 
            origin_address.S_ZIP as Zip1, dest_address.S_CITY as Destination,
            dest_address.S_STATE as State2, dest_address.S_ZIP as Zip2, 
            CONCAT(dest_address.S_CITY, ", ", dest_address.S_STATE) as Destination_State, orders.stage as Stage,
            COUNT(*) as ShipmentCount 
        FROM orders 
        LEFT JOIN address origin_address ON origin_address.S_ORDER = orders.T_ORDER AND origin_address.S_TYPE="O" 
        LEFT JOIN address dest_address ON dest_address.S_ORDER = orders.T_ORDER AND dest_address.S_TYPE="D"
        LEFT JOIN orders_reg_info ON orders_reg_info.R_ORDER = orders.T_ORDER 
        WHERE orders.T_PICKUP BETWEEN :start_date AND :end_date
        AND orders.stage NOT IN ('APPO', 'INV') 
    '''

    if from_weights_value is not None and from_weights_value != -1:
        query += f' AND orders.T_AWEIGHT BETWEEN {from_weights_value} AND {to_weights_value} '
    if zip_code is not None:
        query += ' AND origin_address.S_ZIP = :zip_code '
    if shipment_value is not None and shipment_value != 'All':
        query += ' AND orders.t_div = :shipment_value '

    # Only include stage filter if stage list is provided and has values
    if stage and any(stage):  # Checks if stage is not empty and has valid values
        query += ' AND orders.stage IN :stage '

    query += '''
        GROUP BY origin_address.S_STATE
        ORDER BY ShipmentCount DESC;
    '''

    sql = text(query)
    params = {
        "start_date": start_date,
        "end_date": end_date,
        "zip_code": zip_code,
        "shipment_value": shipment_value,
        "stage": tuple(stage) if stage and any(stage) else None  # Pass as tuple only if stage has values
    }

    result = db.execute(sql, params)
    get_data = []
    cities_data = pd.DataFrame(pd.read_csv('uscitiesdataset/uscities_updated.csv'))

    for row in result:
        item = {
            "Zip1": row.Zip1,
            "State": row.State1,
            "Origin_State": row.Origin_State,
            "ShipmentCount": row.ShipmentCount,
            "lat": 0.0,
            "lng": 0,
        }
        
        if any(cities_data['city_state'].str.contains(row.Origin_State)):
            zip_info = cities_data[cities_data['city_state'].str.contains(row.Origin_State)]
            item["lat"] = float(zip_info.iloc[0]['lat'])
            item["lng"] = float(zip_info.iloc[0]['lng'])
        
        get_data.append(item)

    return get_data


@app.get("/countdestinationshipments", response_model=List[CountResults])
def get_zipcodes_with_most_destinationshipments(
    start_date: date,
    end_date: date,
    from_weights_value: Optional[int] = None,
    to_weights_value: Optional[int] = None,
    zip_code: Optional[str] = None,
    shipment_value: Optional[str] = Query(None),
    stage: Optional[List[str]] = Query(None),  # Allow stage to be a list of strings
    db: Session = Depends(get_db)
):
    query = '''
        SELECT 
            orders.t_div, orders.T_ORDER as Ship, orders.T_AID as Customer, orders.T_AID as AID, 
            orders.T_PIECES as Pcs, orders.T_AWEIGHT as Weight, orders_reg_info.CARRIER as Carriers,
            orders.T_PICKUP as Pickup, orders.T_DELIV Deliv, origin_address.S_CITY Origin,  
            origin_address.S_STATE State1, CONCAT(origin_address.S_CITY, ", ", origin_address.S_STATE) as Origin_State, 
            origin_address.S_ZIP as Zip1, dest_address.S_CITY Destination, dest_address.S_STATE State2, 
            dest_address.S_ZIP as Zip2, CONCAT(dest_address.S_CITY, ", ", dest_address.S_STATE) as Destination_State, 
            orders.stage as Stage, COUNT(*) as ShipmentCount 
        FROM orders 
        LEFT JOIN address origin_address ON origin_address.S_ORDER = orders.T_ORDER AND origin_address.S_TYPE="O" 
        LEFT JOIN address dest_address ON dest_address.S_ORDER = orders.T_ORDER AND dest_address.S_TYPE="D"
        LEFT JOIN orders_reg_info ON orders_reg_info.R_ORDER = orders.T_ORDER 
        WHERE orders.T_PICKUP BETWEEN :start_date AND :end_date
        AND orders.stage NOT IN ('APPO', 'INV') 

    '''

    if from_weights_value is not None and from_weights_value != -1:
        query += f' AND orders.T_AWEIGHT BETWEEN {from_weights_value} AND {to_weights_value}'
    if zip_code is not None:
        query += ' AND dest_address.S_ZIP = :zip_code'
    if shipment_value is not None and shipment_value != 'All':
        query += ' AND orders.t_div = :shipment_value'

    # Include multiple stages filter only if stage is provided and non-empty
    if stage:
        query += ' AND orders.stage IN :stage'

    query += '''
        GROUP BY dest_address.S_STATE
        ORDER BY ShipmentCount DESC;
    '''

    sql = text(query)
    params = {
        "start_date": start_date,
        "end_date": end_date,
        "zip_code": zip_code,
        "shipment_value": shipment_value,
        "stage": tuple(stage) if stage else None  
    }

    result = db.execute(sql, params)
    get_data = []
    cities_data = pd.DataFrame(pd.read_csv('uscitiesdataset/uscities_updated.csv'))
    
    for row in result:
        item = {
            "Zip2": row.Zip2,
            "State2": row.State2,
            "Destination_State": row.Destination_State,
            "ShipmentCount": row.ShipmentCount,
            "Stage": row.Stage,
            "lat": 0.0,
            "lng": 0.0,
        }

        if any(cities_data['city_state'].str.contains(f'^{row.Destination_State}$', case=False, na=False)):
            zip_info = cities_data[cities_data['city_state'].str.contains(f'^{row.Destination_State}$', case=False, na=False)]
            if not zip_info.empty:  # Ensure there's at least one match
                item["lat"] = float(zip_info.iloc[0]['lat'])
                item["lng"] = float(zip_info.iloc[0]['lng'])
            else:
                print(f"No precise match found for state: {row.Destination_State}")
        else:
            print(f"State {row.Destination_State} not found in cities_data.")


        get_data.append(item)

    return get_data












@app.get("/get_data_from_database", response_model=List[DataItem])
def get_data_from_database(
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db)
):

    sql = text(f'''
        SELECT  orders.t_div, orders.T_ORDER as Ship, orders.T_AID as Customer, orders.T_AID as AID, orders.T_PIECES as Pcs, orders.T_AWEIGHT as Weight, orders_reg_info.CARRIER as Carriers,
        orders.T_PICKUP as Pickup, orders.T_DELIV Deliv, origin_address.S_CITY Origin,  origin_address.S_STATE State1, CONCAT(origin_address.S_CITY, ", ", origin_address.S_STATE) as Origin_State, origin_address.S_ZIP as Zip1, dest_address.S_CITY Destination,
        dest_address.S_STATE State2, dest_address.S_ZIP as Zip2, CONCAT(dest_address.S_CITY, ", ", dest_address.S_STATE) as Destination_State, orders.stage FROM orders 
        LEFT JOIN address origin_address ON origin_address.S_ORDER = orders.T_ORDER AND origin_address.S_TYPE="O" 
        LEFT join address dest_address ON dest_address.S_ORDER = orders.T_ORDER AND dest_address.S_TYPE="D"
        LEFT JOIN orders_reg_info ON orders_reg_info.R_ORDER=orders.T_ORDER 
        WHERE orders.T_PICKUP BETWEEN :start_date AND :end_date ;
               ''')


    result = db.execute(sql, {"start_date": start_date, "end_date": end_date})
    get_data = []
    for row in result:

        item = {
            "t_div": row.t_div,
            "Ship": row.Ship,
            "Customer":row.Customer,
            "AID": row.AID,
            "Pcs": row.Pcs,
            "Weight": row.Weight,
            "Carriers": row.Carriers,
            "Pickup": row.Pickup,
            "Deliv": row.Deliv,
            "Origin": row.Origin,
            "Origin_State": row.Origin_State,
            "State1": row.State1,
            "Zip1": row.Zip1,
            "Destination": row.Destination,
            "State2": row.State2,
            "Destination_State": row.Destination_State,
            "Zip2": row.Zip2,
            "stage":row.stage

        }

        get_data.append(item)


    return get_data

from datetime import datetime

def fetch_data_by_t_order(db: Session, t_order: str) -> List[Dict]:
    sql = text('''
        SELECT  orders.t_div, orders.T_ORDER as Ship, orders.T_AID as Customer, orders.T_AID as AID, orders.T_PIECES as Pcs, orders.T_AWEIGHT as Weight, orders_reg_info.CARRIER as Carriers,
        orders.T_PICKUP as Pickup, orders.T_DELIV as Deliv, origin_address.S_CITY as Origin, origin_address.S_STATE as State1, CONCAT(origin_address.S_CITY, ", ", origin_address.S_STATE) as Origin_State, origin_address.S_ZIP as Zip1, dest_address.S_CITY as Destination,
        dest_address.S_STATE as State2, dest_address.S_ZIP as Zip2, CONCAT(dest_address.S_CITY, ", ", dest_address.S_STATE) as Destination_State, orders.stage
        FROM orders 
        LEFT JOIN address origin_address ON origin_address.S_ORDER = orders.T_ORDER AND origin_address.S_TYPE="O" 
        LEFT JOIN address dest_address ON dest_address.S_ORDER = orders.T_ORDER AND dest_address.S_TYPE="D"
        LEFT JOIN orders_reg_info ON orders_reg_info.R_ORDER = orders.T_ORDER 
        WHERE orders.T_ORDER = :t_order;
    ''')

    rows = db.execute(sql, {"t_order": t_order}).fetchall()

    data = []
    for row in rows:


        data.append({
            "t_div": row.t_div,
            "Ship": row.Ship,
            "Customer": row.Customer,
            "AID": row.AID,
            "Pcs": row.Pcs,
            "Weight": row.Weight,
            "Carriers": row.Carriers,
            "Pickup": row.Pickup,
            "Deliv": row.Deliv,
            "Origin": row.Origin,
            "Origin_State": row.Origin_State,
            "State1": row.State1,
            "Zip1": row.Zip1,
            "Destination": row.Destination,
            "State2": row.State2,
            "Destination_State": row.Destination_State,
            "Zip2": row.Zip2,
            "stage": row.stage,
        })

    return data


@app.get("/search_by_t_order")
def search_by_t_order(t_order: str, db: Session = Depends(get_db)):
    return fetch_data_by_t_order(db, t_order)


def fetch_data_by_origin_state_and_date(db: Session, state: str, start_date: str, end_date: str,from_weights_value: Optional[float] = None,
    to_weights_value: Optional[float] = None,
    zip_code: Optional[str] = None,
    shipment_value: Optional[str] = None,
    stage: Optional[List[str]] = None,) -> List[Dict]:
    query = '''
        SELECT  orders.t_div, orders.T_ORDER as Ship, orders.T_AID as Customer, orders.T_AID as AID, 
                orders.T_PIECES as Pcs, orders.T_AWEIGHT as Weight, orders_reg_info.CARRIER as Carriers,
                orders.T_PICKUP as Pickup, orders.T_DELIV as Deliv, origin_address.S_CITY as Origin, 
                origin_address.S_STATE as State1, CONCAT(origin_address.S_CITY, ", ", origin_address.S_STATE) as Origin_State, 
                origin_address.S_ZIP as Zip1, dest_address.S_CITY as Destination, dest_address.S_STATE as State2, 
                dest_address.S_ZIP as Zip2, CONCAT(dest_address.S_CITY, ", ", dest_address.S_STATE) as Destination_State, 
                orders.stage
        FROM orders 
        LEFT JOIN address origin_address ON origin_address.S_ORDER = orders.T_ORDER AND origin_address.S_TYPE="O" 
        LEFT JOIN address dest_address ON dest_address.S_ORDER = orders.T_ORDER AND dest_address.S_TYPE="D"
        LEFT JOIN orders_reg_info ON orders_reg_info.R_ORDER = orders.T_ORDER 
        WHERE origin_address.S_STATE = :state AND orders.T_PICKUP BETWEEN :start_date AND :end_date
        AND orders.stage NOT IN ('APPO', 'INV') 

    '''

    if from_weights_value is not None and to_weights_value is not None:
        query += f' AND orders.T_AWEIGHT BETWEEN :from_weights_value AND :to_weights_value'
    if zip_code is not None:
        query += ' AND dest_address.S_ZIP = :zip_code'
    if shipment_value is not None and shipment_value != 'All':
        query += ' AND orders.t_div = :shipment_value'
    if stage:
        query += ' AND orders.stage IN :stage'

    # Prepare parameters
    params = {
        "state": state,
        "start_date": start_date,
        "end_date": end_date,
    }
    if from_weights_value is not None and to_weights_value is not None and from_weights_value != -1 and  to_weights_value != -1:
        params["from_weights_value"] = from_weights_value
        params["to_weights_value"] = to_weights_value
    if zip_code is not None:
        params["zip_code"] = zip_code
    if shipment_value is not None and shipment_value != "All":
        params["shipment_value"] = shipment_value
    if stage:
        params["stage"] = tuple(stage)  # Convert list to tuple for SQL compatibility

    # Execute query
    sql = text(query)
    rows = db.execute(sql, params).fetchall()

    # Process results
    data = []
    for row in rows:
        data.append({
            "t_div": row.t_div,
            "Ship": row.Ship,
            "Customer": row.Customer,
            "AID": row.AID,
            "Pcs": row.Pcs,
            "Weight": row.Weight,
            "Carriers": row.Carriers,
            "Pickup": row.Pickup,
            "Deliv": row.Deliv,
            "Origin": row.Origin,
            "Origin_State": row.Origin_State,
            "State1": row.State1,
            "Zip1": row.Zip1,
            "Destination": row.Destination,
            "State2": row.State2,
            "Destination_State": row.Destination_State,
            "Zip2": row.Zip2,
            "stage": row.stage,
        })

    return data

@app.get("/search_by_origin_state_and_date")
def search_by_state_and_date(    state: str,
    start_date: str,
    end_date: str,
    from_weights_value: Optional[float] = Query(None),
    to_weights_value: Optional[float] = Query(None),
    zip_code: Optional[str] = Query(None),
    shipment_value: Optional[str] = Query(None),
    stage: Optional[List[str]] = Query(None),
    db: Session = Depends(get_db),):
    return fetch_data_by_origin_state_and_date(       
        db=db,
        state=state,
        start_date=start_date,
        end_date=end_date,
        from_weights_value=from_weights_value,
        to_weights_value=to_weights_value,
        zip_code=zip_code,
        shipment_value=shipment_value,
        stage=stage,)

def fetch_data_by_destination_state_and_date(
    db: Session,
    state: str,
    start_date: str,
    end_date: str,
    from_weights_value: Optional[float] = None,
    to_weights_value: Optional[float] = None,
    zip_code: Optional[str] = None,
    shipment_value: Optional[str] = None,
    stage: Optional[List[str]] = None,
) -> List[Dict]:
    query = '''
        SELECT  orders.t_div, orders.T_ORDER as Ship, orders.T_AID as Customer, orders.T_AID as AID, 
                orders.T_PIECES as Pcs, orders.T_AWEIGHT as Weight, orders_reg_info.CARRIER as Carriers,
                orders.T_PICKUP as Pickup, orders.T_DELIV as Deliv, origin_address.S_CITY as Origin, 
                origin_address.S_STATE as State1, CONCAT(origin_address.S_CITY, ", ", origin_address.S_STATE) as Origin_State, 
                origin_address.S_ZIP as Zip1, dest_address.S_CITY as Destination, dest_address.S_STATE as State2, 
                dest_address.S_ZIP as Zip2, CONCAT(dest_address.S_CITY, ", ", dest_address.S_STATE) as Destination_State, 
                orders.stage
        FROM orders 
        LEFT JOIN address origin_address ON origin_address.S_ORDER = orders.T_ORDER AND origin_address.S_TYPE="O" 
        LEFT JOIN address dest_address ON dest_address.S_ORDER = orders.T_ORDER AND dest_address.S_TYPE="D"
        LEFT JOIN orders_reg_info ON orders_reg_info.R_ORDER = orders.T_ORDER 
        WHERE dest_address.S_STATE = :state AND orders.T_PICKUP BETWEEN :start_date AND :end_date
    '''
    if from_weights_value is not None and to_weights_value is not None and from_weights_value != -1 and  to_weights_value != -1:
        query += f' AND orders.T_AWEIGHT BETWEEN :from_weights_value AND :to_weights_value'
    if zip_code is not None:
        query += ' AND dest_address.S_ZIP = :zip_code'
    if shipment_value is not None and shipment_value != 'All':
        query += ' AND orders.t_div = :shipment_value'
    if stage:
        query += ' AND orders.stage IN :stage'

    params = {
        "state": state,
        "start_date": start_date,
        "end_date": end_date,
    }
    if from_weights_value is not None and to_weights_value is not None:
        params["from_weights_value"] = from_weights_value
        params["to_weights_value"] = to_weights_value
    if zip_code is not None:
        params["zip_code"] = zip_code
    if shipment_value is not None and shipment_value != "All":
        params["shipment_value"] = shipment_value
    if stage:
        params["stage"] = tuple(stage)  
        
    sql = text(query)
    rows = db.execute(sql, params).fetchall()

    data = []
    for row in rows:
        data.append({
            "t_div": row.t_div,
            "Ship": row.Ship,
            "Customer": row.Customer,
            "AID": row.AID,
            "Pcs": row.Pcs,
            "Weight": row.Weight,
            "Carriers": row.Carriers,
            "Pickup": row.Pickup,
            "Deliv": row.Deliv,
            "Origin": row.Origin,
            "Origin_State": row.Origin_State,
            "State1": row.State1,
            "Zip1": row.Zip1,
            "Destination": row.Destination,
            "State2": row.State2,
            "Destination_State": row.Destination_State,
            "Zip2": row.Zip2,
            "stage": row.stage,
        })

    return data

@app.get("/search_by_destination_state_and_date")
def search_by_destination_state_and_date(
    state: str,
    start_date: str,
    end_date: str,
    from_weights_value: Optional[float] = Query(None),
    to_weights_value: Optional[float] = Query(None),
    zip_code: Optional[str] = Query(None),
    shipment_value: Optional[str] = Query(None),
    stage: Optional[List[str]] = Query(None),
    db: Session = Depends(get_db),
):
    return fetch_data_by_destination_state_and_date(
        db=db,
        state=state,
        start_date=start_date,
        end_date=end_date,
        from_weights_value=from_weights_value,
        to_weights_value=to_weights_value,
        zip_code=zip_code,
        shipment_value=shipment_value,
        stage=stage,
    )
mapbox_token = "pk.eyJ1IjoiYmxlbmRpZ2FzaGkiLCJhIjoiY2w4eWV0ajRzMGcxNDNwcG5zbzlmN3o0aCJ9.7yV-xeDHbSiCKg-zlNjU7g"
zipcodeapi_key = 'iMC3Eap57GMVyFI1oC2pljyT5JLtIxGjibvAMmcthhWyhVhAlwXkRt1vNOgQ3UhA'


@app.get("/date_picker_range")
def update_date_picker_range(selected_option: str = Query(..., description="Selected date range option")):
    today = datetime.now().date()
    start_date = None
    end_date = None

    if selected_option == 'today':
        start_date = today
        end_date = today
    elif selected_option == 'yesterday':
        start_date = today - timedelta(days=1)
        end_date = today - timedelta(days=1)
    elif selected_option == 'last_7_days':
        start_date = today - timedelta(days=6)
        end_date = today
    elif selected_option == 'last_30_days':
        start_date = today - timedelta(days=29)
        end_date = today
    elif selected_option == 'this_month':
        start_date = today.replace(day=1)
        end_date = today
    elif selected_option == 'last_month':
        last_month = today.replace(day=1) - timedelta(days=1)
        start_date = last_month.replace(day=1)
        end_date = last_month
    elif selected_option == 'last_3_months':
        last_month = today.replace(day=1) - timedelta(days=1)
        three_months_ago = last_month - timedelta(days=89)
        start_date = three_months_ago.replace(day=1)
        end_date = last_month
    elif selected_option == 'last_year':
        last_year = today.replace(day=1, month=1) - timedelta(days=1)
        start_date = last_year.replace(month=1, day=1)
        end_date = last_year
    else:
        start_date = (datetime.now() - timedelta(days=29)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')

    return {"start_date": start_date, "end_date": end_date}

@app.get("/weights_filter")
def update_weights_range(selected_weights_option: str = Query(..., description="Selected weight range option")):
    from_weights_value = None
    to_weights_value = None

    if selected_weights_option == '0-500':
        from_weights_value = 0
        to_weights_value = 500
    elif selected_weights_option == '500-1000':
        from_weights_value = 500
        to_weights_value = 1000
    elif selected_weights_option == '1000-2000':
        from_weights_value = 1000
        to_weights_value = 2000
    elif selected_weights_option == '2000-5000':
        from_weights_value = 2000
        to_weights_value = 5000
    elif selected_weights_option == '5000-10000':
        from_weights_value = 5000
        to_weights_value = 10000
    elif selected_weights_option == '100000-':
        from_weights_value = 100000

    return {"from_weights_value": from_weights_value, "to_weights_value": to_weights_value}

@app.get('/redis')
def fetch_zip_codes(zip_code: str, radius_value: int, zipcodeapi_key: str):
    r=redis.Redis(host='redis', port=6379, decode_responses=True)
    cached_data = r.hget(zip_code, radius_value)

    if cached_data:
        return json.loads(cached_data)
    response = requests.get(
        f"https://www.zipcodeapi.com/rest/{zipcodeapi_key}/radius.json/{zip_code}/{radius_value}/mile"
    ).json()

    zip_codes_data = {
        'zip_codes': [
            {
                'zip_code': entry['zip_code'],
                'distance': entry['distance'],
                'city': entry['city'],
                'state': entry['state'],
            }
            for entry in response.get('zip_codes', [])
        ]
    }
    r.hset(zip_code, radius_value, json.dumps(zip_codes_data))
    return zip_codes_data 


# @app.get("/filter-data")
# def get_filtered_data(
#     start_date: Optional[str] = None,
#     end_date: Optional[str] = None,
#     from_weights_value: Optional[int] = None,
#     to_weights_value: Optional[int] = None,
#     logistic_activity_value: Optional[str] = None,
#     shipment_value: Optional[str] = Query(None),
#     zip_code: Optional[str] = None,
#     distance_origin_value: Optional[str] = None,
#     radius_value: Optional[int] = None,
#     stage:Optional[str] = None,

#     db: Session = Depends(get_db)
# ):
#     new_data = pd.DataFrame(get_data_from_database(start_date, end_date, db))
#     cities_data = pd.DataFrame(pd.read_csv('uscitiesdataset/uscities_updated.csv'))
    
#     if zip_code is None or zip_code == '0':
#         raise HTTPException(status_code=400, detail="Invalid zip code")
    
#     start_date = pd.to_datetime(start_date) if start_date else None
#     end_date = pd.to_datetime(end_date) if end_date else None

#     # print(new_data['Pickup'])

#     new_data = new_data[new_data['Pickup'].notnull() & (new_data['Pickup'] != '0000-00-00 00:00:00')]
    
#     # print(new_data['Pickup'])

#     new_data['Pickup'] = pd.to_datetime(new_data['Pickup'])

#     new_data = new_data[(new_data['Pickup'] >= start_date) & (new_data['Pickup'] <= end_date)]

#     list_of_cities = [] 
#     list_of_destination_cities=[]
#     print(new_data['Zip1'])

#     if zip_code is not None and radius_value is not None and radius_value >= 0:        
#         # response_zip_codes = requests.get(
#         #     f"https://www.zipcodeapi.com/rest/{zipcodeapi_key}/radius.json/{zip_code}/{radius_value}/mile"
#         # ).json()
        
#         response_zip_codes=fetch_zip_codes(zip_code,radius_value, zipcodeapi_key='iMC3Eap57GMVyFI1oC2pljyT5JLtIxGjibvAMmcthhWyhVhAlwXkRt1vNOgQ3UhA',)

#         if 'zip_codes' in response_zip_codes:
#             zip_codes = [x['zip_code'] for x in response_zip_codes['zip_codes']]
           
#             new_data = new_data[new_data['Zip1'].isin(zip_codes)]
#         if zip_code and distance_origin_value:
#             if int(distance_origin_value) > 0:
#                 radius = 4000
#                 if int(distance_origin_value) == 1:
#                     radius = 500
#                 elif int(distance_origin_value) == 2:
#                     radius = 1000
#                 elif int(distance_origin_value) == 3:
#                     radius = 2000
#                 elif int(distance_origin_value) == 4:
#                     radius = 3000

#                # response_zip_codes = requests.get(
#                 #     f"https://www.zipcodeapi.com/rest/{zipcodeapi_key}/radius.json/{zip_code}/{radius_value}/mile"
#                 # ).json()
#                 response_zip_codes = fetch_zip_codes(zip_code,radius_value,zipcodeapi_key='iMC3Eap57GMVyFI1oC2pljyT5JLtIxGjibvAMmcthhWyhVhAlwXkRt1vNOgQ3UhA')

#             if 'zip_codes' in response_zip_codes:
#                 destination_zip_codes = set(new_data['Zip2'])
#                 for entry in response_zip_codes['zip_codes']:
#                     zip_code = entry.get('zip_code')
#                     if zip_code in destination_zip_codes:
#                         cities = cities_data[cities_data['zips'].str.contains(zip_code, na=False)][['city', 'state_id']]
#                         for city, state_id in cities.values:
#                             list_of_cities.append(f"{city}, {state_id}")
    
#     if logistic_activity_value == 'outbound':
#         location_column = 'Origin_State'
#     else:
#         location_column = 'Destination_State'
    
#         new_data = new_data[new_data[location_column].isin(list_of_cities)]
   
#     from_weights_value = int(from_weights_value)
#     to_weights_value = int(to_weights_value)
#     if from_weights_value== -1:
#         new_data = new_data
#     else:
#         new_data = new_data[(new_data['Weight'] >= from_weights_value) & (new_data['Weight'] <= to_weights_value)]
#     # weights_value = int(weights_value)
#     # if weights_value == -1:
#     #     new_data = new_data  
#     # elif int(weights_value) ==1:
#     #     new_data = new_data[new_data['Weight'].astype(int) < 500]
#     # elif int(weights_value) ==2:
#     #     new_data = new_data[
#     #         (new_data['Weight'].astype(int) > 500) & (new_data['Weight'].astype(int) < 1000)
#     #     ]
#     # elif int(weights_value) ==3:
#     #     new_data = new_data[(new_data['Weight'].astype(int) > 1000) & (new_data['Weight'].astype(int) < 2000)]
#     # elif int(weights_value) ==4:
#     #     new_data = new_data[(new_data['Weight'].astype(int) > 2000) & (new_data['Weight'].astype(int) < 5000)]
#     # elif int(weights_value) ==5:
#     #     new_data = new_data[(new_data['Weight'].astype(int) > 5000) & (new_data['Weight'].astype(int) < 10000)]
#     # elif int(weights_value) ==6:
#     #     new_data = new_data[new_data['Weight'].astype(int) > 10000]
    
#     if shipment_value:
#         if 'All' not in shipment_value and len(shipment_value) > 0:
#             # new_data = [item for item in new_data if 'Div' in item and item['Div'] in shipment_value]
#             new_data = new_data[new_data['t_div'].isin([shipment_value])]
#     if stage:
#         stages = stage.split(",")  # Convert to list
#         new_data = new_data[new_data['stage'].isin(stages)]

#     data_json = new_data.to_dict(orient="records")
#     return data_json


# @app.get("/get_filtered_data_for_multiple_zipcodes")
# def get_filtered_data_for_multiple_zipcodes(
#     zip_codes: Optional[str] = None,
#     start_date: Optional[str] = None,
#     end_date: Optional[str] = None,
#     from_weights_value: Optional[int] = None,
#     to_weights_value: Optional[int] = None,
#     logistic_activity_value: Optional[str] = None,
#     shipment_value: Optional[str] = None,
#     distance_origin_value: Optional[str] = None,
#     radius_value: Optional[int] = None,
#     stage: Optional[str] = None,
#     db: Session = Depends(get_db)
# ):
#     # If zip codes are provided, split them into a list. Otherwise, default to an empty list.
#     if zip_codes:
#         zip_codes = [code.strip() for code in zip_codes.split(',')]
#     else:
#         zip_codes = []  # Use an empty list if no zip codes are provided

#     results = {}

#     # If zip codes are provided, fetch data for each zip code.
#     if zip_codes:
#         for zip_code in zip_codes:
#             result = get_filtered_data(
#                 start_date=start_date,
#                 end_date=end_date,
#                 from_weights_value=from_weights_value,
#                 to_weights_value=to_weights_value,
#                 logistic_activity_value=logistic_activity_value,
#                 shipment_value=shipment_value,
#                 zip_code=zip_code,
#                 distance_origin_value=distance_origin_value,
#                 radius_value=radius_value,
#                 stage=stage,
#                 db=db
#             )
            
#             if not result:  # Check if the result dictionary is empty
#                 results[zip_code] = "No data found for this zip code"
#             else:
#                 results[zip_code] = result
#     else:
#         # If no zip codes are provided, fetch data without zip code filtering.
#         result = get_filtered_data(
#             start_date=start_date,
#             end_date=end_date,
#             from_weights_value=from_weights_value,
#             to_weights_value=to_weights_value,
#             logistic_activity_value=logistic_activity_value,
#             shipment_value=shipment_value,
#             zip_code=None,  # No specific zip code filtering
#             distance_origin_value=distance_origin_value,
#             radius_value=radius_value,
#             stage=stage,
#             db=db
#         )
#         if not result:  # Check if the result dictionary is empty
#             results['all'] = "No data found"
#         else:
#             results['all'] = result

#     return results


@app.get("/route_dataa")
def get_route_dataa(
    order_id: str,
    zip_code: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    from_weights_value: Optional[int] = None,
    to_weights_value: Optional[int] = None,
    logistic_activity_value: Optional[str] = None,
    shipment_value: Optional[str] = None,
    distance_origin_value: Optional[str] = None,
    radius_value: Optional[int] = None,
    stage: Optional[str] = None,
    db: Session = Depends(get_db)
):
    # Load the cities data
    cities_data = pd.read_csv('uscitiesdataset/uscities_updated.csv')

    # Normalize city and state names for comparison
    cities_data['city'] = cities_data['city'].str.strip().str.lower()
    cities_data['state_name'] = cities_data['state_name'].str.strip().str.lower()
    cities_data['state_id'] = cities_data['state_id'].str.strip().str.upper()

    # Step 1: Get filtered data (all shipments in the selected date range and other filters)
    filtered_data = pd.DataFrame(get_filtered_data(
        start_date=start_date,
        end_date=end_date,
        from_weights_value=from_weights_value,
        to_weights_value=to_weights_value,
        logistic_activity_value=logistic_activity_value,
        shipment_value=shipment_value,
        zip_code=zip_code,
        distance_origin_value=distance_origin_value,
        radius_value=radius_value,
        stage=stage,
        db=db
    ))

    # 
    def get_coordinates(city_state: str, cities_data: pd.DataFrame):
        """
        Finds coordinates for a given city and state. If not found in the provided cities_data DataFrame,
        it queries the Mapbox API to retrieve the coordinates.

        Parameters:
            city_state (str): A string containing the city and state, separated by a comma (e.g., "San Francisco, CA").
            cities_data (pd.DataFrame): A DataFrame containing city, state, lat, and lng data.

        Returns:
            str: A string with the coordinates in the format "lng,lat" or None if not found.
        """
        # Split city and state
        city_state_split = city_state.split(", ")
        city = city_state_split[0]
        state = city_state_split[1] if len(city_state_split) > 1 else None

        # Normalize the city and state names for comparison
        city_lower = city.lower()
        state_upper = state.upper() if state else None

        # Find coordinates with strict matching on city and state
        if state:
            coords = cities_data[
                (cities_data['city'] == city_lower) & 
                ((cities_data['state_name'] == state.lower()) | 
                (cities_data['state_id'] == state_upper))
            ]
        else:
            coords = cities_data[cities_data['city'] == city_lower]

        # If coordinates are found in the DataFrame
        if not coords.empty:
            lat = coords.iloc[0]['lat']
            lng = coords.iloc[0]['lng']
            return f"{lng},{lat}"

        # If not found, fallback to Mapbox API
        else:
            return get_coordinates_from_mapbox(city_state)

    # Fallback function to query Mapbox API
    def get_coordinates_from_mapbox(query: str) -> str:
        """
        Queries the Mapbox API to retrieve coordinates for a given location.

        Parameters:
            query (str): The location to search for (e.g., "San Francisco, CA").

        Returns:
            str: A string with the coordinates in the format "lng,lat" or None if not found.
        """
        # Mapbox API URL and access token
        mapbox_url = "https://api.mapbox.com/search/searchbox/v1/forward"
        access_token = "pk.eyJ1IjoiYmxlbmRpZ2FzaGkiLCJhIjoiY2w4eWV0ajRzMGcxNDNwcG5zbzlmN3o0aCJ9.7yV-xeDHbSiCKg-zlNjU7g"
        
        # Query parameters
        params = {
            'q': query,
            'access_token': access_token
        }

        try:
            # Make the API request
            response = requests.get(mapbox_url, params=params)
            response.raise_for_status()  # Raise an error for bad responses

            # Parse the response JSON
            data = response.json()
            if 'features' in data and len(data['features']) > 0:
                # Extract coordinates from the first feature
                coordinates = data['features'][0]['geometry']['coordinates']
                lng, lat = coordinates
                print("tresttd--------------------------------------")
                return f"{lng},{lat}"

        except requests.RequestException as e:
            print(f"Error querying Mapbox API: {e}")

        # Return None if no coordinates are found or an error occurs
        return None

    # Step 2: Get the selected order by order_id
    filtered_data['Ship'] = filtered_data['Ship'].astype(str)
    order_id = str(order_id).strip()

    # Step 2: Find the selected order
    selected_order = filtered_data[filtered_data['Ship'] == order_id]

    if selected_order.empty:
        raise HTTPException(status_code=404, detail="Order not found in the filtered data.")


    # Get origin and destination coordinates
    order_origin_coords = get_coordinates(selected_order.iloc[0]['Origin'], cities_data)
    order_destination_coords = get_coordinates(selected_order.iloc[0]['Destination'], cities_data)

    if not order_origin_coords:
        raise HTTPException(status_code=404, detail=f"Origin coordinates not found for order {order_id}.")
    if not order_destination_coords:
        raise HTTPException(status_code=404, detail=f"Destination coordinates not found for order {order_id}.")

    # Step 3: Call Mapbox API for directions
    mapbox_url = f"https://api.mapbox.com/directions/v5/mapbox/driving/{order_origin_coords};{order_destination_coords}"
    response = requests.get(mapbox_url, params={
        "steps": "true",
        "access_token": mapbox_token
    })
    print(mapbox_url)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Error retrieving route data from Mapbox.")

    route_data = response.json()
    waypoints = [
        (step['maneuver']['location'][1], step['maneuver']['location'][0])
        for leg in route_data['routes'][0]['legs'] for step in leg['steps']
    ]

    # Step 4: Filter shipments based on proximity to waypoints
    PROXIMITY_THRESHOLD_KM = 10.0
    matching_orders = []
    
    for _, order in filtered_data.iterrows():
        # Get origin and destination coordinates for the current order
        order_origin_coords = get_coordinates(order['Origin'], cities_data)
        order_destination_coords = get_coordinates(order['Destination'], cities_data)

        if not order_origin_coords or not order_destination_coords:
            continue  # Skip orders without valid coordinates

        # Check if either the origin or destination of the order is near any of the waypoints
        for waypoint in waypoints:
            waypoint_coords = (waypoint[0], waypoint[1])

            if geodesic((float(order_origin_coords.split(",")[1]), float(order_origin_coords.split(",")[0])), waypoint_coords).km <= PROXIMITY_THRESHOLD_KM or \
            geodesic((float(order_destination_coords.split(",")[1]), float(order_destination_coords.split(",")[0])), waypoint_coords).km <= PROXIMITY_THRESHOLD_KM:
                matching_orders.append(order.to_dict())
                break  # Move to the next order once a match is found

    return {"selected_order": selected_order.iloc[0].to_dict(), "matching_orders": matching_orders}

cities_data = pd.DataFrame(pd.read_csv('uscitiesdataset/uscities_updated.csv'))


@app.get("/get_chart_data")
def get_chart_data(
    start_date: str,
    end_date: str,
    from_weights_value:int,
    to_weights_value:int,
    logistic_activity_value: str,
    shipment_value: str,
    distance_origin_value: float,
    radius_value: int,
    zip_codes: Optional[str] = None,
    stage:Optional[str] = None,
    selected_row_ids: Optional[List[str]] = Query(None), 
    db: Session = Depends(get_db)
):
    zip_codes_list = zip_codes.split(',') if zip_codes else []

    lat_lon_data = []  
    
    for zip_code in zip_codes_list or [""]:
        new_data_df = get_filtered_data_for_multiple_zipcodes(
            zip_codes=zip_code,
            start_date=start_date,
            end_date=end_date,
            from_weights_value=from_weights_value,
            to_weights_value=to_weights_value,
            logistic_activity_value=logistic_activity_value,
            shipment_value=shipment_value,
            distance_origin_value=distance_origin_value,
            radius_value=radius_value,
            stage=stage,
            db=db
        )

        valid_dataframes = []

        for zip_code, zip_code_data in new_data_df.items():
            if len(zip_code_data) > 0:
                zip_code_dataframe = pd.DataFrame(zip_code_data)
                valid_dataframes.append(zip_code_dataframe)

        new_data = pd.concat(valid_dataframes, ignore_index=True)

        new_data['id'] = new_data['Ship']
 
        origin_destination_geo_data = []

        for row in new_data.groupby(['Origin_State', 'Destination_State']):
            origin_city_name = row[0][0]
            origin_city_location = cities_data[cities_data['city_state'].str.match(origin_city_name, na=False, case=False)].values
            destination_city_name = row[0][1]
            destination_city_location = cities_data[
                cities_data['city_state'].str.match(destination_city_name, na=False, case=False)].values

            if len(origin_city_location) == 0 or len(destination_city_location) == 0:
                continue
            origin_city_geo = [origin_city_location[0][6], origin_city_location[0][7]]
            destination_city_geo = [destination_city_location[0][6], destination_city_location[0][7]]
            origin_destination_geo_data.append([
                origin_city_name,
                origin_city_geo,
                destination_city_name,
                destination_city_geo,
                len(row[1]),
                row[1]['Weight'].astype(float),
                row[1]['Ship']
            ])

        max_no_orders = 0
        for sublist in origin_destination_geo_data:
            if sublist[4] > max_no_orders:
                max_no_orders = sublist[4]
        if max_no_orders > 10:
            max_no_orders = 10
        fig5 = go.Figure()
        for i in range(len(origin_destination_geo_data)):
            marker_width = 1 + int(origin_destination_geo_data[i][4]) / max_no_orders

            color = 'black'
            if selected_row_ids is not None:
                if any(row_id in origin_destination_geo_data[i][6] for row_id in selected_row_ids):
                    color = 'red'
                else:
                    color = 'black'
            fig5.add_trace(
                go.Scattermapbox(
                    mode='text+markers+lines',
                    lat=[origin_destination_geo_data[i][1][0], origin_destination_geo_data[i][3][0]],
                    lon=[origin_destination_geo_data[i][1][1], origin_destination_geo_data[i][3][1]],
                    line=dict(width=marker_width, color=color),
                    marker={'size': marker_width + 5},
                    textposition='top right',
                    name=str(origin_destination_geo_data[i][0]) + " " + str(origin_destination_geo_data[i][2]),
                    hovertextsrc="test1",
                    text="" + str(origin_destination_geo_data[i][0])  + str(origin_destination_geo_data[i][2])  +
                         'Orders: ' + str(origin_destination_geo_data[i][4]),
                    hoverinfo='text',
                    hovertext="" + str(origin_destination_geo_data[i][0])  + str(origin_destination_geo_data[i][2])  +
                              'Min. weight: ' + str(min(origin_destination_geo_data[i][5]))  + "\n" +
                              'Max. weight: ' + str(max(origin_destination_geo_data[i][5]))  + "\n" +
                              'Avg. weight: ' + str(
                            round(sum(origin_destination_geo_data[i][5]) / len(origin_destination_geo_data[i][5]))) + "\n" +
                              ' '.join(str(origin_destination_geo_data[i][6].values)),

                )
            )
            if selected_row_ids is not None:
                if any(row_id in origin_destination_geo_data[i][6] for row_id in selected_row_ids):
                    fig5.update_traces(line=dict(color='red'), selector=f"line_{i}")

        fig5.update_layout(
            title='Feb. 2011 American Airline flight paths',
            margin={'l': 0, 't': 0, 'b': 0, 'r': 0},
            hovermode='closest',
            showlegend=False,
            geo_scope='usa',
            mapbox={
                'accesstoken': mapbox_token,
                'center': {'lon': -90.00, 'lat': 40.639},
                'style': 'light',
                'zoom': 4
            }
            
        )

        
        for trace in fig5.data:
            lat_lon_data.append({
                "lat": trace.lat,
                "lon": trace.lon,
                "hovertext": trace.hovertext,
                "zip_code": zip_code
            })

    return JSONResponse(content=lat_lon_data)

from collections import defaultdict















@app.get("/get_filtered_data_for_multiple_zipcodes")
def get_filtered_data_for_multiple_zipcodes(
    zip_codes: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    from_weights_value: Optional[int] = None,
    to_weights_value: Optional[int] = None,
    logistic_activity_value: Optional[str] = None,
    shipment_value: Optional[str] = None,
    distance_origin_value: Optional[str] = None,
    radius_value: Optional[int] = None,
    stage: Optional[str] = None,
    db: Session = Depends(get_db)
):
    # If no zip codes are provided, handle it appropriately
    if zip_codes:
        zip_codes = [code.strip() for code in zip_codes.split(',')]
    else:
        zip_codes = []  # Use an empty list if no zip codes are provided

    results = {}

    # If zip codes are provided, filter by them, else, skip the zip code filtering
    if zip_codes:
        for zip_code in zip_codes:
            result = get_filtered_data(
                start_date=start_date,
                end_date=end_date,
                from_weights_value=from_weights_value,
                to_weights_value=to_weights_value,
                logistic_activity_value=logistic_activity_value,
                shipment_value=shipment_value,
                zip_code=zip_code,
                distance_origin_value=distance_origin_value,
                radius_value=radius_value,
                stage=stage,
                db=db
            )
            results[zip_code] = result
    else:
        # If no zip codes, process data without filtering by zip code
        result = get_filtered_data(
            start_date=start_date,
            end_date=end_date,
            from_weights_value=from_weights_value,
            to_weights_value=to_weights_value,
            logistic_activity_value=logistic_activity_value,
            shipment_value=shipment_value,
            zip_code=None,  # No specific zip code filtering
            distance_origin_value=distance_origin_value,
            radius_value=radius_value,
            stage=stage,
            db=db
        )
        # You can assign the result to a default key or return it as a whole
        results['all'] = result

    return results


@app.get("/filter-data")
def get_filtered_data(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    from_weights_value: Optional[int] = None,
    to_weights_value: Optional[int] = None,
    logistic_activity_value: Optional[str] = None,
    shipment_value: Optional[str] = Query(None),
    zip_code: Optional[str] = None,
    distance_origin_value: Optional[str] = None,
    radius_value: Optional[int] = None,
    stage: Optional[str] = None,
    db: Session = Depends(get_db)
):
    new_data = pd.DataFrame(get_data_from_database(start_date, end_date, db))
    cities_data = pd.DataFrame(pd.read_csv('uscitiesdataset/uscities_updated.csv'))
    
    start_date = pd.to_datetime(start_date) if start_date else None
    end_date = pd.to_datetime(end_date) if end_date else None

    new_data = new_data[new_data['Pickup'].notnull() & (new_data['Pickup'] != '0000-00-00 00:00:00')]
    new_data['Pickup'] = pd.to_datetime(new_data['Pickup'])
    new_data = new_data[(new_data['Pickup'] >= start_date) & (new_data['Pickup'] <= end_date)]

    list_of_cities = []
    list_of_destination_cities = []
    
    if zip_code and radius_value is not None and radius_value >= 0:
        response_zip_codes = fetch_zip_codes(zip_code, radius_value, zipcodeapi_key='iMC3Eap57GMVyFI1oC2pljyT5JLtIxGjibvAMmcthhWyhVhAlwXkRt1vNOgQ3UhA')

        if 'zip_codes' in response_zip_codes:
            zip_codes = [x['zip_code'] for x in response_zip_codes['zip_codes']]
            new_data = new_data[new_data['Zip1'].isin(zip_codes)]
        
        if distance_origin_value:
            radius = 4000
            if int(distance_origin_value) == 1:
                radius = 500
            elif int(distance_origin_value) == 2:
                radius = 1000
            elif int(distance_origin_value) == 3:
                radius = 2000
            elif int(distance_origin_value) == 4:
                radius = 3000
            
            response_zip_codes = fetch_zip_codes(zip_code, radius_value, zipcodeapi_key='iMC3Eap57GMVyFI1oC2pljyT5JLtIxGjibvAMmcthhWyhVhAlwXkRt1vNOgQ3UhA')
            
            if 'zip_codes' in response_zip_codes:
                destination_zip_codes = set(new_data['Zip2'])
                for entry in response_zip_codes['zip_codes']:
                    zip_code = entry.get('zip_code')
                    if zip_code in destination_zip_codes:
                        cities = cities_data[cities_data['zips'].str.contains(zip_code, na=False)][['city', 'state_id']]
                        for city, state_id in cities.values:
                            list_of_cities.append(f"{city}, {state_id}")
    if logistic_activity_value == 'outbound':
        location_column = 'Origin_State'
    else:
        location_column = 'Destination_State'
    
    if list_of_cities:
        new_data = new_data[new_data[location_column].isin(list_of_cities)]
    
    from_weights_value = int(from_weights_value)
    to_weights_value = int(to_weights_value)
    if from_weights_value== -1:
        new_data = new_data
    else:
        new_data = new_data[(new_data['Weight'] >= from_weights_value) & (new_data['Weight'] <= to_weights_value)]
    print(new_data)
    
    if shipment_value and 'All' not in shipment_value:
        new_data = new_data[new_data['t_div'].isin([shipment_value])]
    excluded_stages = ['APPO', 'INV']
    new_data = new_data[~new_data['stage'].isin(excluded_stages)]
    
    if stage:
        stages = stage.split(",")
        new_data = new_data[new_data['stage'].isin(stages)]
 # Group by Zip1
    # grouped_data = defaultdict(list)
    # for _, row in new_data.iterrows():
    #     grouped_data[row['Zip1']].append(row.to_dict())

    # # Convert to JSON format
    # data_json = dict(grouped_data)
    # return data_json
    data_json = new_data.to_dict(orient="records")
    return data_json

# ONLY FOR ONE COUSTUMER 
# @app.get("/get_filtered_data_excluding_customer")
# def get_filtered_data_excluding_customer(
#     customer_name: str,
#     zip_codes: Optional[str] = None,
#     start_date: Optional[str] = None,
#     end_date: Optional[str] = None,
#     from_weights_value: Optional[int] = None,
#     to_weights_value: Optional[int] = None,
#     logistic_activity_value: Optional[str] = None,
#     shipment_value: Optional[str] = None,
#     distance_origin_value: Optional[str] = None,
#     radius_value: Optional[int] = None,
#     stage: Optional[str] = None,
#     db: Session = Depends(get_db)
# ):
#     # Parse zip codes if provided
#     if zip_codes:
#         zip_codes = [code.strip() for code in zip_codes.split(',')]
#     else:
#         zip_codes = []  # Empty list if no zip codes provided

#     results = {}

#     if zip_codes:
#         # Process data for each zip code
#         for zip_code in zip_codes:
#             result = get_filtered_data(
#                 start_date=start_date,
#                 end_date=end_date,
#                 from_weights_value=from_weights_value,
#                 to_weights_value=to_weights_value,
#                 logistic_activity_value=logistic_activity_value,
#                 shipment_value=shipment_value,
#                 zip_code=zip_code,
#                 distance_origin_value=distance_origin_value,
#                 radius_value=radius_value,
#                 stage=stage,
#                 db=db
#             )
#             # Exclude rows where the customer name matches the given value
#             filtered_result = [row for row in result if row.get("Customer") != customer_name]
#             results[zip_code] = filtered_result
#     else:
#         # Process data without zip code filtering
#         result = get_filtered_data(
#             start_date=start_date,
#             end_date=end_date,
#             from_weights_value=from_weights_value,
#             to_weights_value=to_weights_value,
#             logistic_activity_value=logistic_activity_value,
#             shipment_value=shipment_value,
#             zip_code=None,  # No specific zip code filtering
#             distance_origin_value=distance_origin_value,
#             radius_value=radius_value,
#             stage=stage,
#             db=db
#         )
#         # Exclude rows where the customer name matches the given value
#         filtered_result = [row for row in result if row.get("Customer") != customer_name]
#         results["all"] = filtered_result

#     return results
@app.get("/get_filtered_data_excluding_customer")
def get_filtered_data_excluding_customer(
    customer_name: Optional[str] = None,  # Comma-separated list of customer names
    zip_codes: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    from_weights_value: Optional[int] = None,
    to_weights_value: Optional[int] = None,
    logistic_activity_value: Optional[str] = None,
    shipment_value: Optional[str] = None,
    distance_origin_value: Optional[str] = None,
    radius_value: Optional[int] = None,
    stage: Optional[str] = None,
    db: Session = Depends(get_db)
):
    # Parse customer names if provided
    if customer_name:
        customer_name = [name.strip() for name in customer_name.split(',')]
    else:
        customer_name = []  # Empty list if no customer names provided

    # Parse zip codes if provided
    if zip_codes:
        zip_codes = [code.strip() for code in zip_codes.split(',')]
    else:
        zip_codes = []  # Empty list if no zip codes provided

    results = {}
    print(results)
    if zip_codes:
        # Process data for each zip code
        for zip_code in zip_codes:
            result = get_filtered_data(
                start_date=start_date,
                end_date=end_date,
                from_weights_value=from_weights_value,
                to_weights_value=to_weights_value,
                logistic_activity_value=logistic_activity_value,
                shipment_value=shipment_value,
                zip_code=zip_code,
                distance_origin_value=distance_origin_value,
                radius_value=radius_value,
                stage=stage,
                db=db
            )
            # Exclude rows where the customer name matches any in the list
            filtered_result = [
                row for row in result if row.get("Customer") not in customer_name
            ]
            results[zip_code] = filtered_result
    else:
        # Process data without zip code filtering
        result = get_filtered_data(
            start_date=start_date,
            end_date=end_date,
            from_weights_value=from_weights_value,
            to_weights_value=to_weights_value,
            logistic_activity_value=logistic_activity_value,
            shipment_value=shipment_value,
            zip_code=None,  # No specific zip code filtering
            distance_origin_value=distance_origin_value,
            radius_value=radius_value,
            stage=stage,
            db=db
        )
        # Exclude rows where the customer name matches any in the list
        filtered_result = [
            row for row in result if row.get("Customer") not in customer_name
        ]
        results["all"] = filtered_result
    print(results)

    return results



# me e bo me ni file tjeter edhe me bo check per tjetren 
# import csv
# class CityRow(BaseModel):
#     city: str
#     city_ascii: str
#     state_id: Optional[str] = "N/A"
#     state_name: Optional[str] = "N/A"
#     county_fips: Optional[str] = "N/A"
#     county_name: Optional[str] = "N/A"
#     lat: Optional[float] = None
#     lng: Optional[float] = None
#     population: Optional[int] = 0
#     density: Optional[float] = 0.0
#     source: Optional[str] = "Mapbox API"
#     military: Optional[str] = "N/A"
#     incorporated: Optional[str] = "N/A"
#     timezone: Optional[str] = "N/A"
#     ranking: Optional[int] = 0
#     zips: Optional[str] = "N/A"
#     id: Optional[str] = "N/A"
#     city_state: Optional[str] = "N/A"

#     class Config:
#         # This will ensure that the optional fields can be left out in the request
#         min_anystr_length = 1
#         anystr_strip_whitespace = True
# CSV_FILE_PATH = "C:\\Users\\hygerta.hulaj\\Desktop\\MoveIT_refactor\\backend\\uscitiesdataset\\uscities_updated.csv"

# @app.post("/append-to-csv")
# def append_to_csv(row: CityRow):
#     try:
#         # Try to open the file in append mode
#         with open(CSV_FILE_PATH, mode="a", newline="") as file:
#             writer = csv.writer(file)
#             writer.writerow([
#                 row.city, row.city_ascii, row.state_id, row.state_name, 
#                 row.county_fips, row.county_name, row.lat, row.lng, 
#                 row.population, row.density, row.source, row.military, 
#                 row.incorporated, row.timezone, row.ranking, row.zips, 
#                 row.id, row.city_state
#             ])
#         return {"message": "Row appended successfully"}
    
#     except PermissionError:
#         # If the file is open and locked by another program
#         raise HTTPException(status_code=400, detail="File is currently open in another application and cannot be written to. Please close the file and try again.")
    
#     except OSError as e:
#         # Handle other OS-related errors
#         raise HTTPException(status_code=500, detail=f"File operation error: {str(e)}")
    
#     except Exception as e:
#         # General exception handler for other errors
#         raise HTTPException(status_code=500, detail=f"Error appending row: {str(e)}")
# Define your model class
import csv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import os



# Define your model class
class CityRow(BaseModel):
    city: str
    city_ascii: str
    state_id: Optional[str] = "N/A"
    state_name: Optional[str] = "N/A"
    county_fips: Optional[str] = "N/A"
    county_name: Optional[str] = "N/A"
    lat: Optional[float] = None
    lng: Optional[float] = None
    population: Optional[int] = 0
    density: Optional[float] = 0.0
    source: Optional[str] = "Mapbox API"
    military: Optional[str] = "N/A"
    incorporated: Optional[str] = "N/A"
    timezone: Optional[str] = "N/A"
    ranking: Optional[int] = 0
    zips: Optional[str] = "N/A"
    id: Optional[str] = "N/A"
    city_state: Optional[str] = "N/A"

    class Config:
        min_anystr_length = 1
        anystr_strip_whitespace = True

# Specify the new CSV file path
CSV_FILE_PATH = "C:\\Users\\hygerta.hulaj\\Desktop\\MoveIT_refactor\\backend\\uscitiesdataset\\uscities_new.csv"

@app.post("/append-to-csv")
def append_to_csv(row: CityRow):
    try:
        # Check if the CSV file exists, create it if not
        file_exists = os.path.exists(CSV_FILE_PATH)
        
        # Open the file in append mode (if it exists), otherwise create a new one
        with open(CSV_FILE_PATH, mode="a", newline="") as file:
            writer = csv.writer(file)

            # If the file doesn't exist, write the header first
            if not file_exists:
                writer.writerow([
                    "city", "city_ascii", "state_id", "state_name", "county_fips", "county_name", "lat", "lng",
                    "population", "density", "source", "military", "incorporated", "timezone", "ranking", "zips",
                    "id", "city_state"
                ])

            # Write the new row
            writer.writerow([
                row.city, row.city_ascii, row.state_id, row.state_name, 
                row.county_fips, row.county_name, row.lat, row.lng, 
                row.population, row.density, row.source, row.military, 
                row.incorporated, row.timezone, row.ranking, row.zips, 
                row.id, row.city_state
            ])
        
        return {"message": "Row appended successfully"}

    except PermissionError:
        # If the file is open and locked by another program
        raise HTTPException(status_code=400, detail="File is currently open in another application and cannot be written to. Please close the file and try again.")
    
    except OSError as e:
        # Handle other OS-related errors
        raise HTTPException(status_code=500, detail=f"File operation error: {str(e)}")
    
    except Exception as e:
        # General exception handler for other errors
        raise HTTPException(status_code=500, detail=f"Error appending row: {str(e)}")

@app.post("/append-to-csvtest")
def append_to_csv(row: CityRow):
    try:
        with open(CSV_FILE_PATH, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Test City", "Test City", "N/A", "N/A", "N/A", "N/A", 0, 0, 0, 0, "API", "N/A", "N/A", "N/A", 0, "N/A", "N/A", "Test City, N/A"])
        return {"message": "Row appended successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error appending row: {str(e)}")

# class CityRow(BaseModel):
#     city: str
#     city_ascii: str
#     state_id: str
#     state_name: str
#     lat: float
#     lng: float
#     source: str
#     city_state: str

# # Path to the CSV file
# CSV_FILE_PATH = "C:\\Users\\hygerta.hulaj\\Desktop\\MoveIT_refactor\\backend\\uscitiesdataset\\uscities_updated.csv"

# @app.post("/append-to-csv")
# async def append_to_csv(row: dict):
    
#     try:
#         # Prepare the row with default values for missing fields
#         new_row = [
#             row.get("city", "Unknown City"),       # city
#             row.get("city_ascii", "Unknown City"),# city_ascii
#             row.get("state_id", "N/A"),           # state_id
#             row.get("state_name", "N/A"),         # state_name
#             row.get("county_fips", ""),           # county_fips
#             row.get("county_name", ""),           # county_name
#             row.get("lat", ""),                   # lat
#             row.get("lng", ""),                   # lng
#             row.get("population", ""),            # population
#             row.get("density", ""),               # density
#             row.get("source", ""),                # source
#             row.get("military", ""),              # military
#             row.get("incorporated", ""),          # incorporated
#             row.get("timezone", ""),              # timezone
#             row.get("ranking", ""),               # ranking
#             row.get("zips", ""),                  # zips
#             row.get("id", ""),                    # id
#             row.get("city_state", "Unknown City, N/A"), # city_state
#         ]

#         # Append the row to the CSV
#         with open(CSV_FILE_PATH, mode="a", newline="") as file:
#             writer = csv.writer(file)
#             writer.writerow(new_row)
        
#         return {"message": "Row appended successfully"}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to append row: {e}")





















# Create the FastAPI app

# # Helper function to query Mapbox API
def get_coordinates_from_mapbox(query: str) -> str:
    """
    Queries the Mapbox API to retrieve coordinates for a given location.

    Parameters:
        query (str): The location to search for (e.g., "San Francisco, CA").

    Returns:
        str: A string with the coordinates in the format "lng,lat" or None if not found.
    """
    # Mapbox API URL and access token
    mapbox_url = "https://api.mapbox.com/search/searchbox/v1/forward"
    access_token = "pk.eyJ1IjoiYmxlbmRpZ2FzaGkiLCJhIjoiY2w4eWV0ajRzMGcxNDNwcG5zbzlmN3o0aCJ9.7yV-xeDHbSiCKg-zlNjU7g"
    
    # Query parameters
    params = {
        'q': query,
        'access_token': access_token
    }

    try:
        # Make the API request
        response = requests.get(mapbox_url, params=params)
        response.raise_for_status()  # Raise an error for bad responses

        # Parse the response JSON
        data = response.json()
        if 'features' in data and len(data['features']) > 0:
            # Extract coordinates from the first feature
            coordinates = data['features'][0]['geometry']['coordinates']
            lng, lat = coordinates
            return f"{lng},{lat}"

    except requests.RequestException as e:
        print(f"Error querying Mapbox API: {e}")

    # Return None if no coordinates are found or an error occurs
    return None

# Endpoint for getting coordinates
@app.get("/coordinates", summary="Get Coordinates from Mapbox")
async def fetch_coordinates(query: str = Query(..., description="Location to search for (e.g., 'San Francisco, CA')")):
    """
    Fetch coordinates for a given location using the Mapbox API.

    Parameters:
        query (str): The location to search for.

    Returns:
        A dictionary containing the longitude and latitude, or a message if not found.
    """
    coordinates = get_coordinates_from_mapbox(query)
    if coordinates:
        lng, lat = coordinates.split(",")
        return {"longitude": float(lng), "latitude": float(lat)}
    return {"error": "Coordinates not found for the given location"}



from fastapi import FastAPI, Query
from pydantic import BaseModel
import requests
import math



# Helper function to query Mapbox for coordinates of a location
# async def get_coordinates_from_mapbox(query: str) -> str:
#     """
#     Queries the Mapbox API to retrieve coordinates for a given location.

#     Parameters:
#         query (str): The location to search for (e.g., "San Francisco, CA").

#     Returns:
#         str: A string with the coordinates in the format "lng,lat" or None if not found.
#     """
#     mapbox_url = "https://api.mapbox.com/search/searchbox/v1/forward"
#     access_token = "pk.eyJ1IjoiYmxlbmRpZ2FzaGkiLCJhIjoiY2w4eWV0ajRzMGcxNDNwcG5zbzlmN3o0aCJ9.7yV-xeDHbSiCKg-zlNjU7g"

#     params = {
#         "q": query,
#         "access_token": access_token,
#     }

#     try:
#         response = requests.get(mapbox_url, params=params)
#         response.raise_for_status()
#         data = response.json()
#         if "features" in data and len(data["features"]) > 0:
#             coordinates = data["features"][0]["geometry"]["coordinates"]
#             lng, lat = coordinates
#             return f"{lng},{lat}"
#     except requests.RequestException as e:
#         print(f"Error querying Mapbox API: {e}")
#     return None
from fastapi import FastAPI, Query, HTTPException
import httpx
from haversine import haversine, Unit
from geopy.distance import geodesic

async def get_coordinates_from_mapbox(location: str):
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{location}.json?access_token=pk.eyJ1IjoiYmxlbmRpZ2FzaGkiLCJhIjoiY2w4eWV0ajRzMGcxNDNwcG5zbzlmN3o0aCJ9.7yV-xeDHbSiCKg-zlNjU7g"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()
        return data['features'][0]['center']

@app.get("/routefor5kmm", summary="Get route with coordinates at every 5 km and search for nearby points")
async def fetch_directions_with_radius_search(
    start_location: str = Query(..., description="Starting location (e.g., 'New York, NY')"),
    end_location: str = Query(..., description="Ending location (e.g., 'Boston, MA')"),
    search_radius: int = Query(3, description="Radius in kilometers to search for additional points"),
    interval_km: int = Query(5, description="Interval in kilometers along the route")
):
    try:
        start_coordinates = await get_coordinates_from_mapbox(start_location)
        end_coordinates = await get_coordinates_from_mapbox(end_location)

        # Mapbox API URL
        directions_url = (
            f"https://api.mapbox.com/directions/v5/mapbox/driving/"
            f"{start_coordinates[0]},{start_coordinates[1]};{end_coordinates[0]},{end_coordinates[1]}"
            f"?access_token=pk.eyJ1IjoiYmxlbmRpZ2FzaGkiLCJhIjoiY2w4eWV0ajRzMGcxNDNwcG5zbzlmN3o0aCJ9.7yV-xeDHbSiCKg-zlNjU7g&geometries=geojson"
        )

        # Fetch directions data
        async with httpx.AsyncClient() as client:
            response = await client.get(directions_url)
            response.raise_for_status()
            data = response.json()

        # Extract route coordinates
        coordinates = data['routes'][0]['geometry']['coordinates']

        # Function to calculate points at regular intervals (e.g., 5 km)
        def get_points_at_intervals(coords, interval_km):
            points = [coords[0]]
            cumulative_distance = 0

            for i in range(1, len(coords)):
                segment_distance = geodesic(coords[i - 1][::-1], coords[i][::-1]).kilometers
                cumulative_distance += segment_distance

                if cumulative_distance >= interval_km:
                    points.append(coords[i])
                    cumulative_distance = 0

            return points

        # Get coordinates at specified intervals along the route
        main_route_points = get_points_at_intervals(coordinates, interval_km)

        # Improved function to search nearby points within a radius
        def search_nearby_points(center, radius_km):
            nearby_points = []
            for point in coordinates:  # Using the full route for nearby point search
                distance = haversine(center[::-1], point[::-1], unit=Unit.KILOMETERS)
                if distance <= radius_km:
                    nearby_points.append(point)
            return nearby_points

        # For each point along the route, find nearby points
        result = []
        for point in main_route_points:
            nearby_points = search_nearby_points(point, search_radius)
            print(f"Point: {point}, Search Radius: {search_radius}, Nearby Points: {len(nearby_points)}")
            result.append({
                "route_point": point,
                "nearby_points": nearby_points
            })

        return {"route_points": result}

    except httpx.HTTPStatusError:
        raise HTTPException(status_code=400, detail="Error fetching directions from Mapbox")
    except (IndexError, KeyError):
        raise HTTPException(status_code=500, detail="Unexpected response format from Mapbox")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

# @app.get("/routefor5kmm", summary="Get route with coordinates at every 5 km")
# async def fetch_directions(start_location: str, end_location: str):
#     try:
#         start_coordinates = await get_coordinates_from_mapbox(start_location)
#         end_coordinates = await get_coordinates_from_mapbox(end_location)

#         directions_url = f"https://api.mapbox.com/directions/v5/mapbox/driving/{start_coordinates[0]},{start_coordinates[1]};{end_coordinates[0]},{end_coordinates[1]}?access_token=pk.eyJ1IjoiYmxlbmRpZ2FzaGkiLCJhIjoiY2w4eWV0ajRzMGcxNDNwcG5zbzlmN3o0aCJ9.7yV-xeDHbSiCKg-zlNjU7g&geometries=geojson"

#         async with httpx.AsyncClient() as client:
#             response = await client.get(directions_url)
#             response.raise_for_status()
#             data = response.json()
#             coordinates = data['routes'][0]['geometry']['coordinates']
#             return {"coordinates": coordinates}

#     except httpx.HTTPStatusError as e:
#         raise HTTPException(status_code=400, detail="Error fetching directions")
#     except (IndexError, KeyError) as e:
#         raise HTTPException(status_code=500, detail="Unexpected response format from Mapbox")
# # Helper function to query Mapbox Directions API for a route


def get_route_between_coordinates(start: str, end: str) -> list:
    """
    Queries the Mapbox Directions API to retrieve a route between two points.

    Parameters:
        start (str): The starting coordinates in the format "lng,lat".
        end (str): The ending coordinates in the format "lng,lat".

    Returns:
        list: A list of coordinates (lng, lat) along the route.
    """
    directions_url = "https://api.mapbox.com/directions/v5/mapbox/driving"
    access_token = "pk.eyJ1IjoiYmxlbmRpZ2FzaGkiLCJhIjoiY2w4eWV0ajRzMGcxNDNwcG5zbzlmN3o0aCJ9.7yV-xeDHbSiCKg-zlNjU7g"

    params = {
        "access_token": access_token,
        "geometries": "geojson",
    }

    try:
        response = requests.get(f"{directions_url}/{start};{end}", params=params)
        response.raise_for_status()
        data = response.json()
        if "routes" in data and len(data["routes"]) > 0:
            # Extract the route geometry
            return data["routes"][0]["geometry"]["coordinates"]
    except requests.RequestException as e:
        print(f"Error querying Mapbox Directions API: {e}")
    return []


# Function to calculate intermediate points at every 5 km
def get_intermediate_points(route: list, interval: float = 5.0) -> list:
    """
    Generates intermediate points along a route at a fixed distance interval.

    Parameters:
        route (list): A list of coordinates (lng, lat) along the route.
        interval (float): The distance interval in kilometers.

    Returns:
        list: A list of coordinates (lng, lat) at every interval along the route.
    """
    def haversine_distance(coord1, coord2):
        """
        Calculate the Haversine distance between two coordinates in kilometers.
        """
        R = 6371  # Earth's radius in km
        lng1, lat1 = math.radians(coord1[0]), math.radians(coord1[1])
        lng2, lat2 = math.radians(coord2[0]), math.radians(coord2[1])
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    points = [route[0]]  # Start with the first point
    total_distance = 0.0

    for i in range(1, len(route)):
        segment_distance = haversine_distance(route[i - 1], route[i])
        total_distance += segment_distance
        while total_distance >= interval:
            total_distance -= interval
            # Interpolate the point
            ratio = (interval - total_distance) / segment_distance
            lng = route[i - 1][0] + ratio * (route[i][0] - route[i - 1][0])
            lat = route[i - 1][1] + ratio * (route[i][1] - route[i - 1][1])
            points.append([lng, lat])
    return points


# Endpoint for fetching route coordinates
@app.get("/routefor5km", summary="Get route with coordinates at every 5 km")
async def fetch_route(
    start_location: str = Query(..., description="Starting location (e.g., 'New York, NY')"),
    end_location: str = Query(..., description="Ending location (e.g., 'Boston, MA')"),
):
    """
    Fetch a route between two locations and return coordinates at every 5 km along the route.
    """
    start = await get_coordinates_from_mapbox(start_location)
    end = await get_coordinates_from_mapbox(end_location)

    if not start or not end:
        return {"error": "Could not fetch coordinates for one or both locations."}

    route = get_route_between_coordinates(start, end)

    if not route:
        return {"error": "Could not fetch the route between the specified locations."}

    intermediate_points = get_intermediate_points(route)
    return {"route": intermediate_points}







# @app.get("/matching-orders", summary="Get orders matching locations on route")
# async def get_matching_orders(
#     start_location: str = Query(..., description="Starting location (e.g., 'New York, NY')"),
#     end_location: str = Query(..., description="Ending location (e.g., 'Boston, MA')"),
#     start_date: Optional[str] = None,
#     end_date: Optional[str] = None,
#     from_weights_value: Optional[int] = None,
#     to_weights_value: Optional[int] = None,
#     logistic_activity_value: Optional[str] = None,
#     shipment_value: Optional[str] = None,
#     zip_code: Optional[str] = None,
#     distance_origin_value: Optional[str] = None,
#     radius_value: Optional[int] = None,
#     stage: Optional[str] = None,
#     db: Session = Depends(get_db)
# ):
#     """
#     Fetch orders from `/filter-data` and match their locations with points along the route.
#     """
#     # Fetch filtered orders
#     filtered_data = get_filtered_data(
#         start_date=start_date,
#         end_date=end_date,
#         from_weights_value=from_weights_value,
#         to_weights_value=to_weights_value,
#         logistic_activity_value=logistic_activity_value,
#         shipment_value=shipment_value,
#         zip_code=zip_code,
#         distance_origin_value=distance_origin_value,
#         radius_value=radius_value,
#         stage=stage,
#         db=db
#     )

#     # Convert to DataFrame for easier manipulation
#     orders_df = pd.DataFrame(filtered_data)

#     # Fetch route with intermediate points
#     route_data = await fetch_route(start_location, end_location)

#     if "error" in route_data:
#         return {"error": route_data["error"]}

#     route_coordinates = route_data.get("route", [])

#     route_states = set()

#     # Function to geocode locations and get coordinates
#     def get_coordinates(location):
#         """
#         Get coordinates (longitude, latitude) for a given location using the Mapbox Geocoding API.
#         """
#         mapbox_url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{location}.json"
#         access_token = "pk.eyJ1IjoiYmxlbmRpZ2FzaGkiLCJhIjoiY2w4eWV0ajRzMGcxNDNwcG5zbzlmN3o0aCJ9.7yV-xeDHbSiCKg-zlNjU7g"

#         params = {
#             "access_token": access_token,
#             "limit": 1  # Get only the top result
#         }

#         try:
#             response = requests.get(mapbox_url, params=params)
#             response.raise_for_status()
#             data = response.json()

#             if "features" in data and len(data["features"]) > 0:
#                 coordinates = data["features"][0]["geometry"]["coordinates"]
#                 return tuple(coordinates)  # (lng, lat)
#         except requests.RequestException as e:
#             print(f"Error querying Mapbox Geocoding API: {e}")

#         return None

#     # Get states from route coordinates
#     # for coord in route_coordinates:
#     #     state = get_state_from_coordinates(coord)
#     #     if state:
#     #         route_states.add(state)

#     # Get coordinates and states for orders
#     orders_df["Origin_Coordinates"] = orders_df["Origin_State"].apply(get_coordinates)
#     orders_df["Destination_Coordinates"] = orders_df["Destination_State"].apply(get_coordinates)

#     # orders_df["Origin_State"] = orders_df["Origin_Coordinates"].apply(get_state_from_coordinates)
#     # orders_df["Destination_State"] = orders_df["Destination_Coordinates"].apply(get_state_from_coordinates)

#     # Filter orders matching origin or destination states
#     matching_orders = orders_df[
#         (orders_df["Origin_State"].isin(route_states)) |
#         (orders_df["Destination_State"].isin(route_states))
#     ]

#     return matching_orders.to_dict(orient="records")

import numpy as np

def convert_numpy_types(data):
    if isinstance(data, list):
        return [convert_numpy_types(item) for item in data]
    elif isinstance(data, dict):
        return {key: convert_numpy_types(value) for key, value in data.items()}
    elif isinstance(data, np.int64):
        return int(data)
    return data

from fastapi.responses import JSONResponse
import pandas as pd
from typing import Optional
from sqlalchemy.orm import Session
import asyncio

async def get_coordinates_for_states(states: list):
    """
    Helper function to fetch coordinates for a list of states in parallel.
    This assumes `get_coordinates_from_mapbox` is an async function.
    """
    tasks = [get_coordinates_from_mapbox(state) for state in states]
    return await asyncio.gather(*tasks)

# @app.get("/matching-orders", summary="Get orders matching locations on route")
# async def get_matching_orders(
#     start_date: Optional[str] = None,
#     end_date: Optional[str] = None,
#     from_weights_value: Optional[int] = None,
#     to_weights_value: Optional[int] = None,
#     logistic_activity_value: Optional[str] = None,
#     shipment_value: Optional[str] = None,
#     zip_code: Optional[str] = None,
#     distance_origin_value: Optional[str] = None,
#     radius_value: Optional[int] = 5,
#     stage: Optional[str] = None,
#     db: Session = Depends(get_db)
# ):
#     """
#     Fetch orders from `/filter-data` and match their locations with points along the route.
#     """
#     # Step 1: Fetch filtered orders
#     filtered_data = get_filtered_data(
#         start_date=start_date,
#         end_date=end_date,
#         from_weights_value=from_weights_value,
#         to_weights_value=to_weights_value,
#         logistic_activity_value=logistic_activity_value,
#         shipment_value=shipment_value,
#         zip_code=zip_code,
#         distance_origin_value=distance_origin_value,
#         radius_value=radius_value,
#         stage=stage,
#         db=db
#     )

#     # Convert to DataFrame for manipulation
#     orders_df = pd.DataFrame(filtered_data)

#     # Step 2: Get the list of unique origin and destination states
#     origin_states = orders_df["Origin_State"].unique()
#     destination_states = orders_df["Destination_State"].unique()

#     # Step 3: Fetch coordinates for origin and destination states asynchronously
#     origin_coords, destination_coords = await asyncio.gather(
#         get_coordinates_for_states(origin_states),
#         get_coordinates_for_states(destination_states)
#     )

#     # Step 4: Map the coordinates back to the DataFrame
#     origin_coords_map = dict(zip(origin_states, origin_coords))
#     destination_coords_map = dict(zip(destination_states, destination_coords))

#     # Step 5: Assign the coordinates to the DataFrame
#     orders_df["Origin_Coordinates"] = orders_df["Origin_State"].map(origin_coords_map)
#     orders_df["Destination_Coordinates"] = orders_df["Destination_State"].map(destination_coords_map)

#     # Step 6: Convert datetime columns to strings
#     for column in orders_df.select_dtypes(include=['datetime']):
#         orders_df[column] = orders_df[column].dt.strftime('%Y-%m-%d %H:%M:%S')

#     # Ensure that any datetime-related fields are serializable as strings
#     orders_df = orders_df.applymap(
#         lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if isinstance(x, (pd.Timestamp, datetime)) else x
#     )

#     # Convert DataFrame back to a list of dictionaries
#     orders_list = orders_df.to_dict(orient="records")

#     # Return the response as JSON
#     return JSONResponse(content=orders_list)


# @app.get("/matching-orders", summary="Get orders matching locations on route")
# async def get_matching_orders(
#     start_location: str = Query(..., description="Starting location (e.g., 'New York, NY')"),
#     end_location: str = Query(..., description="Ending location (e.g., 'Boston, MA')"),
#     start_date: Optional[str] = None,
#     end_date: Optional[str] = None,
#     from_weights_value: Optional[int] = None,
#     to_weights_value: Optional[int] = None,
#     logistic_activity_value: Optional[str] = None,
#     shipment_value: Optional[str] = None,
#     zip_code: Optional[str] = None,
#     distance_origin_value: Optional[str] = None,
#     radius_value: Optional[int] = 5,  # Default radius is 5 km
#     stage: Optional[str] = None,
#     db: Session = Depends(get_db),
# ):
#     """
#     Fetch orders and match their locations (origin/destination) with points along a route.
#     """
#     try:
#         # Fetch the route with intermediate points
#         route_response = await fetch_directions(start_location, end_location)
#         print(route_response)
#         if not route_response or "error" in route_response:
#             return JSONResponse(content={"error": route_response.get("error", "Unable to fetch route.")}, status_code=400)

#         route_coordinates = route_response.get("coordinates", [])

#         if not route_coordinates:
#             return JSONResponse(content={"error": "No route found."}, status_code=400)

#         # Convert intermediate points for easier matching
#         intermediate_points = [tuple(point) for point in route_coordinates]

#         # Fetch filtered orders
#         filtered_data = get_filtered_data(
#             start_date=start_date,
#             end_date=end_date,
#             from_weights_value=from_weights_value,
#             to_weights_value=to_weights_value,
#             logistic_activity_value=logistic_activity_value,
#             shipment_value=shipment_value,
#             zip_code=zip_code,
#             distance_origin_value=distance_origin_value,
#             radius_value=radius_value,
#             stage=stage,
#             db=db,
#         )

#         if not filtered_data:
#             return JSONResponse(content={"message": "No matching orders found."}, status_code=200)

#         # Convert to DataFrame for easier manipulation
#         orders_df = pd.DataFrame(filtered_data)

#         # Step 2: Get the list of unique origin and destination states
#         origin_states = orders_df["Origin_State"].unique()
#         destination_states = orders_df["Destination_State"].unique()

#         # Step 3: Fetch coordinates for origin and destination states asynchronously
#         origin_coords, destination_coords = await asyncio.gather(
#             get_coordinates_for_states(origin_states),
#             get_coordinates_for_states(destination_states)
#         )

#         # Step 4: Map the coordinates back to the DataFrame
#         origin_coords_map = dict(zip(origin_states, origin_coords))
#         destination_coords_map = dict(zip(destination_states, destination_coords))

#         # Step 5: Assign the coordinates to the DataFrame
#         orders_df["Origin_Coordinates"] = orders_df["Origin_State"].map(origin_coords_map)
#         orders_df["Destination_Coordinates"] = orders_df["Destination_State"].map(destination_coords_map)

#         # Step 6: Convert datetime columns to strings
#         for column in orders_df.select_dtypes(include=['datetime']):
#             orders_df[column] = orders_df[column].dt.strftime('%Y-%m-%d %H:%M:%S')

#         # Ensure that any datetime-related fields are serializable as strings
#         orders_df = orders_df.applymap(
#             lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if isinstance(x, (pd.Timestamp, datetime)) else x
#         )

#         # Function to check if two coordinates match within a tolerance
#         def coordinates_match(coord1, coord2, tolerance=1):
#             """
#             Check if two coordinates match within a given tolerance.
#             """
#             return abs(coord1[0] - coord2[0]) <= tolerance and abs(coord1[1] - coord2[1]) <= tolerance

#         # Match orders
#         matched_orders = []
#         for _, row in orders_df.iterrows():  # Use iterrows on the DataFrame
#             try:
#                 # Ensure coordinates are tuples
#                 origin_coords = tuple(row["Origin_Coordinates"])  # Directly use the list as a tuple
#                 dest_coords = tuple(row["Destination_Coordinates"])  # Directly use the list as a tuple

#                 # Check if both origin and destination fall within the route coordinates using the tolerance check
#                 origin_matched = any(coordinates_match(origin_coords, point) for point in intermediate_points)
#                 destination_matched = any(coordinates_match(dest_coords, point) for point in intermediate_points)

#                 if origin_matched and destination_matched:
#                     matched_orders.append(row.to_dict())  # Convert row to dictionary here
#             except Exception as e:
#                 print(f"Error processing order row: {row}. Error: {e}")

#         if not matched_orders:
#             print("No orders matched.")
#         return JSONResponse(content=convert_numpy_types(matched_orders), status_code=200)

#     except Exception as e:
#         print(f"Unexpected error: {e}")
#         return JSONResponse(content={"error": "Internal server error"}, status_code=500)

# 55 =km differenc me 0.5
def coordinates_match(coord1, coord2, tolerance=0.3):
    return abs(coord1[0] - coord2[0]) <= tolerance and abs(coord1[1] - coord2[1]) <= tolerance


@app.get("/matching-orders", summary="Get orders matching locations on route")
async def get_matching_orders(
    start_location: str = Query(..., description="Starting location (e.g., 'New York, NY')"),
    end_location: str = Query(..., description="Ending location (e.g., 'Boston, MA')"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    from_weights_value: Optional[int] = None,
    to_weights_value: Optional[int] = None,
    logistic_activity_value: Optional[str] = None,
    shipment_value: Optional[str] = None,
    zip_code: Optional[str] = None,
    distance_origin_value: Optional[str] = None,
    radius_value: Optional[int] = 5,
    stage: Optional[str] = None,
    interval_km:Optional[int] = 5,
    db: Session = Depends(get_db),
):
    """
    Fetch orders and match their locations (origin/destination) with points along a route.
    """
    try:
        # Fetch the route with intermediate points and nearby points
        route_response = await fetch_directions_with_radius_search(start_location, end_location, search_radius=radius_value,interval_km=interval_km)
        
        if not route_response or "error" in route_response:
            return JSONResponse(content={"error": route_response.get("error", "Unable to fetch route.")}, status_code=400)

        route_points_with_nearby = route_response.get("route_points", [])

        if not route_points_with_nearby:
            return JSONResponse(content={"error": "No route found."}, status_code=400)

        # Convert intermediate points with nearby locations for easier matching
        route_coordinates_with_nearby = [
            {'route_point': tuple(item['route_point']), 'nearby_points': [tuple(p) for p in item['nearby_points']]}
            for item in route_points_with_nearby
        ]

        # Fetch filtered orders
        filtered_data =  get_filtered_data(
            start_date=start_date,
            end_date=end_date,
            from_weights_value=from_weights_value,
            to_weights_value=to_weights_value,
            logistic_activity_value=logistic_activity_value,
            shipment_value=shipment_value,
            zip_code=zip_code,
            distance_origin_value=distance_origin_value,
            radius_value=radius_value,
            stage=stage,
            db=db,
        )

        if not filtered_data:
            return JSONResponse(content={"message": "No matching orders found."}, status_code=200)
        filtered_data = [
                order for order in filtered_data
                if order.get("stage", "").strip().upper() != "DONE"
            ]
        # Convert to DataFrame for easier manipulation
        orders_df = pd.DataFrame(filtered_data)

        # Get the list of unique origin and destination states
        origin_states = orders_df["Origin_State"].unique()
        destination_states = orders_df["Destination_State"].unique()

        # Fetch coordinates for origin and destination states asynchronously
        origin_coords, destination_coords = await asyncio.gather(
            get_coordinates_for_states(origin_states),
            get_coordinates_for_states(destination_states)
        )

        # Map the coordinates back to the DataFrame
        origin_coords_map = dict(zip(origin_states, origin_coords))
        destination_coords_map = dict(zip(destination_states, destination_coords))

        # Assign the coordinates to the DataFrame
        orders_df["Origin_Coordinates"] = orders_df["Origin_State"].map(origin_coords_map)
        orders_df["Destination_Coordinates"] = orders_df["Destination_State"].map(destination_coords_map)

        # Convert datetime columns to strings
        orders_df = orders_df.applymap(
            lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if isinstance(x, (pd.Timestamp, datetime)) else x
        )

        matched_orders = []
        for _, row in orders_df.iterrows():
            try:
                origin_coords = tuple(row["Origin_Coordinates"])
                dest_coords = tuple(row["Destination_Coordinates"])

                origin_matched = any(coordinates_match(origin_coords, point['route_point']) or
                                     any(coordinates_match(origin_coords, nearby) for nearby in point['nearby_points'])
                                     for point in route_coordinates_with_nearby)
                destination_matched = any(coordinates_match(dest_coords, point['route_point']) or
                                          any(coordinates_match(dest_coords, nearby) for nearby in point['nearby_points'])
                                          for point in route_coordinates_with_nearby)

                if origin_matched and destination_matched:
                    matched_orders.append(row.to_dict())  # Convert row to dictionary here
            except Exception as e:
                print(f"Error processing order row: {row}. Error: {e}")

        if not matched_orders:
            return JSONResponse(content={"message": "No matching orders found."}, status_code=200)

        return JSONResponse(content=convert_numpy_types(matched_orders), status_code=200)

    except Exception as e:
        print(f"Unexpected error: {e}")
        return JSONResponse(content={"error": "Internal server error"}, status_code=500)


@app.get("/matching-orderssssssssssss", summary="Get orders matching locations on route")
async def get_matching_orders(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    from_weights_value: Optional[int] = None,
    to_weights_value: Optional[int] = None,
    logistic_activity_value: Optional[str] = None,
    shipment_value: Optional[str] = None,
    zip_code: Optional[str] = None,
    distance_origin_value: Optional[str] = None,
    radius_value: Optional[int] = 5,
    stage: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Fetch orders from `/filter-data` and match their locations with points along the route.
    """
    # Step 1: Fetch filtered orders
    filtered_data = get_filtered_data(
        start_date=start_date,
        end_date=end_date,
        from_weights_value=from_weights_value,
        to_weights_value=to_weights_value,
        logistic_activity_value=logistic_activity_value,
        shipment_value=shipment_value,
        zip_code=zip_code,
        distance_origin_value=distance_origin_value,
        radius_value=radius_value,
        stage=stage,
        db=db
    )
    filtered_data = [
        order for order in filtered_data
        if order.get("stage", "").strip().upper() != "DONE"
    ]

    # Convert to DataFrame for manipulation
    orders_df = pd.DataFrame(filtered_data)

    # Step 2: Get the list of unique origin and destination states
    origin_states = orders_df["Origin_State"].unique()
    destination_states = orders_df["Destination_State"].unique()

    # Step 3: Fetch coordinates for origin and destination states asynchronously
    origin_coords, destination_coords = await asyncio.gather(
        get_coordinates_for_states(origin_states),
        get_coordinates_for_states(destination_states)
    )

    # Step 4: Map the coordinates back to the DataFrame
    origin_coords_map = dict(zip(origin_states, origin_coords))
    destination_coords_map = dict(zip(destination_states, destination_coords))

    # Step 5: Assign the coordinates to the DataFrame
    orders_df["Origin_Coordinates"] = orders_df["Origin_State"].map(origin_coords_map)
    orders_df["Destination_Coordinates"] = orders_df["Destination_State"].map(destination_coords_map)

    # Step 6: Convert datetime columns to strings
    for column in orders_df.select_dtypes(include=['datetime']):
        orders_df[column] = orders_df[column].dt.strftime('%Y-%m-%d %H:%M:%S')

    # Ensure that any datetime-related fields are serializable as strings
    orders_df = orders_df.applymap(
        lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if isinstance(x, (pd.Timestamp, datetime)) else x
    )

    # Convert DataFrame back to a list of dictionaries
    orders_list = orders_df.to_dict(orient="records")

    # Return the response as JSON
    return JSONResponse(content=orders_list)



# @app.get("/matching-orderssssssssssss", summary="Get orders matching locations on route")
# async def get_matching_orders(
#     start_date: Optional[str] = None,
#     end_date: Optional[str] = None,
#     from_weights_value: Optional[int] = None,
#     to_weights_value: Optional[int] = None,
#     logistic_activity_value: Optional[str] = None,
#     shipment_value: Optional[str] = None,
#     zip_code: Optional[str] = None,
#     radius_value: Optional[int] = 5,
#     stage: Optional[str] = None,
#     db: Session = Depends(get_db)
# ):
#     """
#     Execute a raw SQL query and match orders' locations with points along the route.
#     """
#     # Step 1: Build the raw SQL query
#     base_query = """
#         SELECT
#             o.t_div AS Division,
#             o.T_ORDER AS Ship,
#             o.T_AID AS Customer,
#             o.T_AID AS AID,
#             o.T_PIECES AS Pcs,
#             o.T_AWEIGHT AS Weight,
#             r.CARRIER AS Carriers,
#             o.T_PICKUP AS Pickup,
#             o.T_DELIV AS Deliv,
#             oa.S_CITY AS Origin,
#             oa.S_STATE AS State1,
#             oa.S_ZIP AS Zip1,
#             da.S_CITY AS Destination,
#             da.S_STATE AS State2,
#             da.S_ZIP AS Zip2,
#             o.stage AS Stage
#         FROM Orders o
#         LEFT JOIN OrdersRegInfo r ON r.R_ORDER = o.T_ORDER
#         LEFT JOIN Address oa ON oa.S_ORDER = o.T_ORDER AND oa.S_TYPE = 'O'
#         LEFT JOIN Address da ON da.S_ORDER = o.T_ORDER AND da.S_TYPE = 'D'
#         WHERE 1 = 1
#     """

#     # Step 2: Add filters dynamically
#     filters = []
#     params = {}

#     if start_date and end_date:
#         filters.append("o.T_PICKUP BETWEEN :start_date AND :end_date")
#         params["start_date"] = start_date
#         params["end_date"] = end_date

#     if shipment_value:
#         filters.append("o.T_ORDER = :shipment_value")
#         params["shipment_value"] = shipment_value

#     if stage and stage.lower() != "done":
#         filters.append("o.stage != 'DONE'")

#     if filters:
#         base_query += " AND " + " AND ".join(filters)

#     # Wrap the query as a text object
#     query = text(base_query)

#     # Step 3: Execute the raw query
#     result = db.execute(query, params).fetchall()

#     # Step 4: Convert the result to a DataFrame
#     orders_df = DataFrame(result, columns=[
#         "Division", "Ship", "Customer", "AID", "Pcs", "Weight", "Carriers",
#         "Pickup", "Deliv", "Origin", "State1", "Zip1", "Destination",
#         "State2", "Zip2", "Stage"
#     ])


#     # Step 5: Get the list of unique origin and destination states
#     origin_states = orders_df["State1"].unique()
#     destination_states = orders_df["State2"].unique()

#     # Step 6: Fetch coordinates for origin and destination states asynchronously
#     origin_coords, destination_coords = await asyncio.gather(
#         get_coordinates_for_states(origin_states),
#         get_coordinates_for_states(destination_states)
#     )

#     # Step 7: Map the coordinates back to the DataFrame
#     origin_coords_map = dict(zip(origin_states, origin_coords))
#     destination_coords_map = dict(zip(destination_states, destination_coords))

#     orders_df["Origin_Coordinates"] = orders_df["State1"].map(origin_coords_map)
#     orders_df["Destination_Coordinates"] = orders_df["State2"].map(destination_coords_map)

#     # Step 8: Convert datetime columns to strings
#     orders_df = orders_df.applymap(
#         lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if isinstance(x, datetime) else x
#     )

#     # Convert DataFrame back to a list of dictionaries
#     orders_list = orders_df.to_dict(orient="records")

#     # Return the response as JSON
#     return JSONResponse(content=orders_list)

# @app.get("/matching-orders", summary="Get orders matching locations on route")
# async def get_matching_orders(
    # start_location: str = Query(..., description="Starting location (e.g., 'New York, NY')"),
    # end_location: str = Query(..., description="Ending location (e.g., 'Boston, MA')"),
#     start_date: Optional[str] = None,
#     end_date: Optional[str] = None,
#     from_weights_value: Optional[int] = None,
#     to_weights_value: Optional[int] = None,
#     logistic_activity_value: Optional[str] = None,
#     shipment_value: Optional[str] = None,
#     zip_code: Optional[str] = None,
#     distance_origin_value: Optional[str] = None,
#     radius_value: Optional[int] = None,
#     stage: Optional[str] = None,
#     db: Session = Depends(get_db)
# ):
#     """
#     Fetch orders from `/filter-data` and match their locations with points along the route.
#     """
#     # Fetch filtered orders
#     filtered_data = get_filtered_data(
#         start_date=start_date,
#         end_date=end_date,
#         from_weights_value=from_weights_value,
#         to_weights_value=to_weights_value,
#         logistic_activity_value=logistic_activity_value,
#         shipment_value=shipment_value,
#         zip_code=zip_code,
#         distance_origin_value=distance_origin_value,
#         radius_value=radius_value,
#         stage=stage,
#         db=db
#     )
    
#     # Convert to DataFrame for easier manipulation
#     orders_df = pd.DataFrame(filtered_data)
#     # print('orders',orders_df)
#     # Fetch route with intermediate points
#     route_data = await fetch_route(start_location, end_location)
    
#     if "error" in route_data:
#         return {"error": route_data["error"]}

#     route_coordinates = route_data.get("route", [])
    
#     route_states = set()

#     # Mock a function to determine the state for a coordinate
#     def get_state_from_coordinates(coord):
#         """
#         Get the state name from coordinates using the Mapbox Geocoding API.

#         Parameters:
#             coord (tuple): A tuple containing longitude and latitude (lng, lat).

#         Returns:
#             str: The name of the state or None if not found.
#         """
#         lng, lat = coord
#         mapbox_url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{lng},{lat}.json"
#         access_token = "pk.eyJ1IjoiYmxlbmRpZ2FzaGkiLCJhIjoiY2w4eWV0ajRzMGcxNDNwcG5zbzlmN3o0aCJ9.7yV-xeDHbSiCKg-zlNjU7g"

#         params = {
#             "access_token": access_token,
#             "types": "region",  # Focus on regions (states, provinces)
#         }

#         try:
#             response = requests.get(mapbox_url, params=params)
#             response.raise_for_status()
#             data = response.json()

#             if "features" in data and len(data["features"]) > 0:
#                 # Extract the state name from the response
#                 state_name = data["features"][0]["text"]
#                 return state_name
#         except requests.RequestException as e:
#             print(f"Error querying Mapbox Geocoding API: {e}")

#         return None

#     # Get states from route coordinates
#     for coord in route_coordinates:
#         state = get_state_from_coordinates(coord)
#         print('orders',state)

#         if state:
#             route_states.add(state)

#     # Filter orders matching origin or destination states
#     matching_orders = orders_df[
#         (orders_df["Origin_State"].isin(route_states)) |
#         (orders_df["Destination_State"].isin(route_states))
#     ]

#     return matching_orders.to_dict(orient="records")


















# import asyncio
# import aiohttp
# # Asynchronous helper function to get coordinates
# async def get_coordinates_from_mapbox_async(session, query: str) -> str:
#     mapbox_url = "https://api.mapbox.com/search/searchbox/v1/forward"
#     access_token = "your_access_token"
    
#     params = {
#         "q": query,
#         "access_token": access_token,
#     }

#     try:
#         async with session.get(mapbox_url, params=params) as response:
#             data = await response.json()
#             if "features" in data and len(data["features"]) > 0:
#                 coordinates = data["features"][0]["geometry"]["coordinates"]
#                 lng, lat = coordinates
#                 return f"{lng},{lat}"
#     except Exception as e:
#         print(f"Error querying Mapbox API: {e}")
#     return None

# # Function to fetch coordinates for all orders concurrently
# async def get_coordinates_for_orders(orders_df):
#     async with aiohttp.ClientSession() as session:
#         tasks = []
#         for index, row in orders_df.iterrows():
#             origin_task = asyncio.ensure_future(get_coordinates_from_mapbox_async(session, row['Origin_State']))
#             destination_task = asyncio.ensure_future(get_coordinates_from_mapbox_async(session, row['Destination_State']))
#             tasks.append((origin_task, destination_task))

#         results = await asyncio.gather(*[task_pair for task_pair in tasks])

#         for i, (origin_res, destination_res) in enumerate(results):
#             orders_df.at[i, 'Origin_Coordinates'] = origin_res
#             orders_df.at[i, 'Destination_Coordinates'] = destination_res

# # Then, use this function
# await get_coordinates_for_orders(orders_df)