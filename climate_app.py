import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
import numpy as np

from flask import Flask,jsonify


#Setup Database
engine = create_engine('sqlite:///Resources/hawaii.sqlite')
Base = automap_base()
Base.prepare(engine, reflect = True)

Measurement = Base.classes.measurement 
Station = Base.classes.station 

session = Session(engine)

app = Flask(__name__)

#Flask Routes

@app.route("/")
def home():
    """Queries from Climate Activity"""
    return(
    f"All Available Routes:<br/>"

    "<br/>"
    f"/api/v1.0/precipitation<br/>"
    f"Precipitation data from previous year<br/>"

    "<br/>"
    f"/api/v1.0/stations<br/>"
    f"List of stations<br/>"

    "<br/>"
    f"/api/v1.0/tobs<br/>"
    f"Dates and temperature data from the most active station of previous year<br/>"

    "<br/>"
    f"/api/v1.0/<start><br/>"
    f"Minimum, average, and maximum temperature from start date<br/>"
    
    "<br/>"
    f"Input requested dates as endpoints (dd-mm-yyy): [start_date]/[end_date]<br/>"
    f"/api/v1.0/<start>/<end><br/>"
    f"Minimum, average, and maximum temperature for given time frame<br/>"
    # Return a JSON list of the minimum temperature, the average temperature, 
    # and the max temperature for a given start or start-end range.

    # When given the start only, calculate TMIN, TAVG, and TMAX for all dates
    # greater than and equal to the start date.

    # When given the start and the end date, calculate the TMIN, TAVG, and TMAX for 
    # dates between the start and end date inclusive.
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    #Find previous year's date
    date_as_result = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = date_as_result[0]
    dt_last_date= dt.datetime.strptime(last_date, '%Y-%m-%d')
    year_before = (dt_last_date) - dt.timedelta(days=365)

    #Find prcp from previous year until last date
    prcp_year_before = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date>=year_before).all()

    yearly_prcp = []
    for date, prcp in prcp_year_before:
        date_prcp_dict={}
        date_prcp_dict['date']= date
        date_prcp_dict['prcp']=prcp
        
        yearly_prcp.append(date_prcp_dict)

    return jsonify(yearly_prcp)

@app.route("/api/v1.0/stations")
def stations():
    station_count = session.query(Station.station).order_by(Station.station).all()
    station_count = station_count[0][0]

    station_list = []
    for station in station_count:
        station_dict={}
        station_dict['Station Name']=station

        station_list.append(station_dict)

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def temperature():
    #redo year_before variable
    date_as_result = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = date_as_result[0]
    dt_last_date= dt.datetime.strptime(last_date, '%Y-%m-%d')
    year_before = (dt_last_date) - dt.timedelta(days=365)
    
    temp_count = session.query(Measurement.station, func.count(Measurement.tobs)).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.tobs).desc()).all()
    temp_count_station= temp_count[0][0]
    previous_temps = session.query(Measurement.tobs).filter(Measurement.station == temp_count_station and Measurement.date >= year_before)

    temp_list=[]
    for temps in previous_temps:
        temp_dict={}
        temp_dict['Temperature']=temps

        temp_list.append(temp_dict)
    return jsonify(temp_list)


@app.route("/api/v1.0/<start_date>/<end_date>")
def start(start_date="",end_date=""):
    if end_date != None:
        start = dt.datetime.strptime(start_date, "%m-%d-%Y").date()
        end = dt.datetime.strptime(end_date, "%m-%d-%Y").date()
        
        start_end_data = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs),func.avg(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
        
        start_date_list = list(start_end_data)
    else:
        start = dt.datetime.strptime(start_date, "%m-%d-%Y").date()
        
        start_data = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs),func.avg(Measurement.tobs)).filter(Measurement.date >= start).all()
        
        start_date_list = list(start_data)
    
    return jsonify(start_date_list[0])


 #   select_date=[08-08]
    # canonicalized = start.replace({select_date}).datetime()
    # for date in temp_data:
    #     search_term = date[""].replace({select_date})
    #     temp_date_dict={}
    #     temp_date_dict['Low'] = session.query(func.min(measurement.tobs).filter(measurement.date >= search_term)


    # if search_term == canonicalized:
    #     return jsonify(select_date)

    # return jsonify(f"Time frame with dates {select_date} not found.")





    # date_of_temp = []
    # for min,max,avg in temp_data:
    #     date_of_temp.append(min)
    #     date_of_temp.append(max)
    #     date_of_temp.append(avg)
    
    # return jsonify(date_of_temp)
   # date = session.query(Measurement.date).all()
    # low_temp = session.query(func.min(Measurement.tobs)).all()
    # high_temp = session.query(func.max(Measurement.tobs)).all()
    # avg_temp = session.query(func.avg(Measurement.tobs)).all()
    # avg_temp = round(avg_temp[0][0], 2)
    # temp_data = list(low_temp, high_temp, avg_temp)
    

if __name__ == "__main__":
    app.run(debug=True)

