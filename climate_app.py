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
    # Convert the query results to a dictionary using date as the key 
    # and prcp as the value.
    #Return the JSON representation of your dictionary.
    "<br/>"
    f"/api/v1.0/stations<br/>"
    f"List of stations<br/>"
    # Return a JSON list of stations from the dataset.
    "<br/>"
    f"/api/v1.0/tobs<br/>"
    f"Dates and temperature data from the most active station of previous year<br/>"
    # Query the dates and temperature observations of the most active station 
    # for the last year of data.
    # Return a JSON list of temperature observations (TOBS) for the previous year.
    "<br/>"
    f"/api/v1.0/<start><br/>"
    f"Minimum, average, and maximum temperature from start date<br/>"
    
    "<br/>"
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

@app.route("/api/v1.0/<start>", defaults={'end': None})
@app.route("/api/v1.0/<start>/<end>")
def startdate_enddate(start,end):
    # date = session.query(Measurement.date).all()
    # low_temp = session.query(func.min(Measurement.tobs)).all()
    # high_temp = session.query(func.max(Measurement.tobs)).all()
    # avg_temp = session.query(func.avg(Measurement.tobs)).all()
    # avg_temp = round(avg_temp[0][0], 2)
    # temp_data = list(low_temp, high_temp, avg_temp)
    
    if end != None:
        temp_data = session.query(func.min(measurement.tobs), (func.max(measurement.tobs),(func.avg(measurement.tobs)).\
            filter(measurement.date <= end).\
            filter(measurement.date >= start).all()
    else:
        temp_data = session.query(func.min(measurement.tobs), (func.max(measurement.tobs),(func.avg(measurement.tobs)).\
            filter(measurement.date >= start).all()

#     date=[]
#     canonicalized = start.replace("").datetime()
#     for date in temp_data:
#         search_term = date[""].replace("")
#         temp_date_dict={}
#         temp_date_dict['Low'] = session.query(func.min(measurement.tobs).filter(measurement.date >= canonicalized)

# #
# #        if search_term == canonicalized:
# #            return jsonify(date)

#     return jsonify({"error": f"Character with real_name {real_name} not found."}), 404







if __name__ == "__main__":
    app.run(debug=True)

