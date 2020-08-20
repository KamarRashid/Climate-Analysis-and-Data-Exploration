# Import Modules
import numpy as np
import pandas as pd
import datetime as dt
from flask import Flask, jsonify

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)
#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all API routes that are available."""
    return(
        "Welcome to the Hawaii Climate API App<br/>"
        "Available API Routes:<br/>"
        "<br/>"
        "-Date and precipitation for the previous year<br/>"
        "/api/v1.0/precipitation<br/>"
        "<br/>"
        "-List of stations from the dataset<br/>"
        "/api/v1.0/stations<br/>"
        "<br/>"
        "-Temperature observations(TOBS) for the previous year<br/>"
        "/api/v1.0/tobs<br/>"
        "<br/>"
        "-Min, Max. and Avg. temperatures for all dates greater than and equal to the given start date: (please use 'yyyy-mm-dd' date format):<br/>"
        "/api/v1.0/start<br/>"
        "<br/>"
        "-Min. Max. and Avg. tempratures for given start and end date: (please use 'yyyy-mm-dd'/'yyyy-mm-dd' date format):<br/>"
        "/api/v1.0/start/end<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the JSON representation of your dictionary."""
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Close session
    session.close()
    # Calculate the date 1 year ago from the last data point in thedatabase
    last_data_point = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    last_date = last_data_point.date

    # Convert last date fron string to date
    last_date = dt.datetime.strptime(last_date, "%Y-%m-%d").date()

    query_date = last_date - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    last_year_prcp = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= query_date).all()

    last_year_prcp_list = list(np.ravel(last_year_prcp))    
    return jsonify(last_year_prcp_list)

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset"""
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Close session
    session.close()

    # List the active stations 
    active_stations = session.query(Station.station, Station.name).all()
    return jsonify(active_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    """Query the dates and temperature observations of the most active station for the last year of data.
    Return a JSON list of temperature observations (TOBS) for the previous year."""
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Close session
    session.close()

    # List the stations and the counts in descending order.
    active_stations = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    
    # Determine the most active station
    most_active_station = active_stations[0][0]

    # Query and calculate the temperature observations
    most_active_temp = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.station == most_active_station).all()

    lowest_temp = most_active_temp[0][0]
    highest_temp = most_active_temp[0][1]
    avg_temp = round(most_active_temp[0][2], 2)

    # Create dictionary of results
    tobs = ({"lowest temp":lowest_temp, "highest temp": highest_temp, "avg temp": avg_temp})
    return jsonify(tobs)

@app.route("/api/v1.0/<start_date>")
def tobs_start(start_date):
    """When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date"""
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Close session
    session.close()

    # Take and convert date to yyyy-mm-dd format for the query
    start_date = dt.datetime.strptime(start_date, '%Y-%m-%d')

    # Query and calculate the temperature observations
    station_temp = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start_date).all()

    lowest_temp = station_temp[0][0]
    highest_temp = station_temp[0][1]
    avg_temp = round(station_temp[0][2], 2)

    # Create dictionary of results
    tobs = ({"lowest temp": lowest_temp,"highest temp": highest_temp, "avg temp": avg_temp})
    return jsonify(tobs)


@app.route("/api/v1.0/<start_date>/<end_date>")
def tobs_start_end(start_date, end_date):
    """When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive."""
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Close session
    session.close()

    # Take and convert date to yyyy-mm-dd format for the query
    start_date = dt.datetime.strptime(start_date, '%Y-%m-%d')
    end_date = dt.datetime.strptime(end_date, '%Y-%m-%d')

    # Query and calculate the temperature observations
    station_temp = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start_date, Measurement.date <= end_date).all()

    lowest_temp = station_temp[0][0]
    highest_temp = station_temp[0][1]
    avg_temp = round(station_temp[0][2], 2)

    # Create dictionary of results
    tobs = ({"Start Date": start_date, "End Date": end_date, "lowest temp": lowest_temp,"highest temp": highest_temp, "avg temp": avg_temp})
    return jsonify(tobs)

if __name__ == '__main__':
    app.run(debug=True)
