import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime

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
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
# 2. Create an app, being sure to pass __name__
app = Flask(__name__)


# 3. Define what to do when a user hits the index route
@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start> (Enter date in YYYY-MM-DD format)<br/>"
        f"/api/v1.0/<start>/<end>"
    )

# 4. Define what to do when a user hits the /about route
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all precipitation readings by date"""
    # Query all precipitation readings
    results = session.query(Measurement.date,Measurement.prcp).all()

    session.close()
    prcp_dt = list(np.ravel(results))

    prcp_dict = {prcp_dt[i]: prcp_dt[i + 1] for i in range(0, len(prcp_dt), 2)}
    
    return jsonify(prcp_dict)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all passenger names"""
    # Query all stations
    results2 = session.query(Measurement.station).\
            group_by(Measurement.station).all()
    session.close()
    station_lst = list(np.ravel(results2))
    
    return jsonify(station_lst)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

#Filter data for last 12 months
    one_yr_data2 = session.query(Measurement.date,Measurement.tobs).filter(Measurement.date> '2016-08-19').\
                filter(Measurement.date< '2017-08-18').filter(Measurement.station== 'USC00519281').all()
    session.close()
# Save the query results as a Pandas DataFrame and set the index to the date column
    one_yr_df2 = list(np.ravel(one_yr_data2))
    
    return jsonify(one_yr_df2)

@app.route("/api/v1.0/<start>")
def startdt(start):
     # Create our session (link) from Python to the DB
    session = Session(engine)
    date_str = start # The date - 29 Dec 2017
    format_str = '%Y-%m-%d' # The format
    dt_str = datetime.datetime.strptime(date_str, format_str)
    qdate = dt_str.date()


    TMAX = session.query(func.max(Measurement.tobs)).filter(Measurement.date >= qdate).all()
    TMIN = session.query(func.min(Measurement.tobs)).filter(Measurement.date >= qdate).all()
    TAVG = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= qdate).all()
    session.close()

    return jsonify(
        f"Temperature stats for starting date : {qdate}. " 
        f"Highest Temperature: {str(TMAX)}. "
        f"Lowest Temperature: {str(TMIN)}. "
        f"Average Temperature: {str(TAVG)}"
    )


@app.route("/api/v1.0/<start>/<end>")
def startenddt(start,end):
     # Create our session (link) from Python to the DB
    session = Session(engine)

    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    results = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    session.close()
    temps = list(np.ravel(results))
    return jsonify(temps)



if __name__ == "__main__":
    app.run(debug=True)
