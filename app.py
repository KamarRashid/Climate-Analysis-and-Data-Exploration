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
        "Available API Routes:<br/>"
        "/api/v1.0/precipitation<br/>"
        "/api/v1.0/stations<br/>"
        "/api/v1.0/tobs<br/>"
        "/api/v1.0/start<br/>"
        "/api/v1.0/start/end<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Calculate the date 1 year ago from the last data point in thedatabase
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    # last_date = dt.datetime.strptime(last_date, "%y-%m-%d")
    
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    # Perform a query to retrieve the data and precipitation scores
    last_year_prcp = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= query_date).all()

    last_year_prcp_list = list(np.ravel(last_year_prcp))    
    return jsonify(last_year_prcp_list)

if __name__ == '__main__':
    app.run(debug=True)
