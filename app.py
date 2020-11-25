import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

# Homepage
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Welcome to the Hawaii Climate Page! Surfs Up!<br/> "
        f"Available Routes:<br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"Stations: /api/v1.0/stations<br/>"
        f"Temperature Observations: /api/v1.0/tobs<br/>"
        f"Temperature stats from the start date: /api/v1.0/yyyy-mm-dd<br/>"
        f"Temperature stats from start to end dates: /api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
    )

# Precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Query all dates and precipitation values
    query_result = session.query(Measurement.date, Measurement.prcp).\
                order_by(Measurement.date).all()
    session.close()

    # Create a dictionary from the row data and append to a list of precipitation
    precipitation = []
    for date, prcp in query_result:
        prcp_dict = {}
        prcp_dict["Date"] = date
        prcp_dict["Precipitation"] = prcp
        precipitation.append(prcp_dict)

    return jsonify(precipitation)

# Stations
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Query all stations
    query_result = session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()
    session.close()

    # Create a dictionary from the row data and append to a list of stations
    stations = []
    for station,name,lat,lon,el in query_result:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_dict["Lat"] = lat
        station_dict["Lon"] = lon
        station_dict["Elevation"] = el
        stations.append(station_dict)

    return jsonify(stations)

# TOBS
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Query dates and temperature observations of the most active station for the last year of data
    latest_str = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    latest_date = dt.datetime.strptime(latest_str, '%Y-%m-%d')
    query_date = dt.date(latest_date.year -1, latest_date.month, latest_date.day)
    query_result = session.query(Measurement.date,Measurement.tobs).filter(Measurement.date >= query_date).all()
    session.close()

    # Create a dictionary from the row data and append to a list of temperature observations
    tobs_all = []
    for date, tobs in query_result:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Tobs"] = tobs
        tobsall.append(tobs_dict)

    return jsonify(tobs_all)

# Start
@app.route("/api/v1.0/<start>")
def temp_range_start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Query for the minimum temperature, the average temperature, and the max temperature for a given start
    query_result =   session.query(  Measurement.date,\
                                func.min(Measurement.tobs), \
                                func.avg(Measurement.tobs), \
                                func.max(Measurement.tobs)).\
                        filter(Measurement.date >= start).\
                        group_by(Measurement.date).all()
    session.close() 

    # Create a dictionary from the row data and append to a list of temperature observations
    tobs_all = []
    for date, min, avg, max in query_result:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["TMIN"] = min
        tobs_dict["TAVG"] = avg
        tobs_dict["TMAX"] = max
        tobs_all.append(tobs_dict)

    return jsonify(tobs_all)


if __name__ == '__main__':
    app.run(debug=True)