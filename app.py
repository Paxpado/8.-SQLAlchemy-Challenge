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
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
### I'm getting an AttributeError on 'measurement' and 'station' - can't seem to solve this issue
# Measurement = Base.classes.measurement
# Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all dates and precipitation
    results = session.query(Base.classes.measurement.date, Base.classes.measurement.prcp).all()

    session.close()

    # Convert to list of dictionaries to jsonify
    prcp_date = []

    for date, prcp in results:
        prcp_date_dict = {}
        prcp_date_dict["date"] = date
        prcp_date_dict["prcp"] = prcp
        prcp_date.append(prcp_date_dict)

    return jsonify(prcp_date)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all stations
    results = session.query(Base.classes.station.station, Base.classes.station.name).all()

    session.close()

    # Convert to list of dictionaries to jsonify
    stations = {}
    for s, name in results:
        stations_dict = {}
        stations_dict["station"]=s
        stations_dict["name"]=name
        stations.append(stations_dict)

    session.close()
 
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # find the recent date and last year's date
    recent_date = session.query(Base.classes.measurement.date).\
        order_by(Base.classes.measurement.date.desc().first())

    last_year = (dt.datetime.strptime(recent_date[0], "%Y-%m-%d") - dt.timedelta(days=365)).strftime('%Y-%m-%d')
    
    # find the most active station
    active_stations = session.query(Base.classes.measurement.station,func.count(Base.classes.measurement.station)).group_by(Base.classes.measurement.station).\
        order_by(func.count(Base.classes.measurement.station).desc()).first()

    # Query the dates and temperature observations of the most active station for the last year of data.
    results = session.query(Base.classes.measurement.tobs).filter(Base.classes.measurement.date >= last_year).\
        filter(Base.classes.measurement.station == active_stations[0]).all()
    
    # List of dictionaries to jsonify
    tobs_list = []

    for date, tobs in results:
        tobs_new_list = {}
        tobs_new_list["date"] = tobs
        tobs_list.append(tobs_new_list)
    
    session.close()

    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def start_date(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of minimum, average and max temperature for a given date"""
    results = session.query(Base.classes.measurement.date,func.min(Base.classes.measurement.tobs),\
         func.avg(Base.classes.measurement.tobs), func.max(Base.classes.measurement.tobs)).\
             filter(Base.classes.measurement.date >= start).all()
             
    session.close()
    
# Create a dictionary from the row data and append to a list of info
    start_list = []
    for date, min, avg, max in results:
        start_new_dict = {}
        start_new_dict["DATE"] = date
        start_new_dict["TMIN"] = min
        start_new_dict["TAVG"] = avg
        start_new_dict["TMAX"] = max
        start_list.append(start_new_dict)

    return jsonify(start_list)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    """Return a list of minimum, average and max temperature for a given start date and end date"""
    # Query of min, max and avg temperature for dates between given start and end date.
    results = session.query(func.min(Base.classes.measurement.tobs),\
         func.avg(Base.classes.measurement.tobs), func.max(Base.classes.measurement.tobs)).\
             filter(Base.classes.measurement.date >= start).filter(Base.classes.measurement.date <= end).all()

    session.close()        
    
# Create a dictionary from the row data and append to a list of info
    start_end_list = []

    for min, avg, max in results:
        start_end_dict = {}
        start_end_dict["TMIN"] = min
        start_end_dict["TAVG"] = avg
        start_end_dict["TMAX "] = max
        start_end_list.append(start_end_dict)



    return jsonify(start_end_list)



if __name__ == "__main__":
    app.run(debug=True)
