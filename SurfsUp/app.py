# Import the dependencies.
from flask import Flask, jsonify

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text, inspect, func
import datetime

import numpy as np
import pandas as pd

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
#Base.classes.keys()
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    return (
        f"Welcome!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&ltstart&gt<br/>"
        f"/api/v1.0/&ltstart&gt/&ltend&gt"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    output = {}

    #Find the first day
    last_day = session.query(measurement.date).order_by(measurement.date.desc()).first()
    day_last_year = datetime.datetime.strptime(str(last_day[0]), '%Y-%m-%d') - datetime.timedelta(days=365)
    day_last_year_str = day_last_year.strftime('%Y-%m-%d')

    sel_data = session.query(measurement.date, measurement.prcp).filter(measurement.date >= day_last_year_str).all()
    df = pd.DataFrame(sel_data, columns=['date', 'precipitation'])
    #df['date'] = pd.to_datetime(df['date'])
    sorted_df = df.sort_values(by=['date'], ascending=True)
    for ind in sorted_df.index:
        output[df['date'][ind]] = df['precipitation'][ind]
        #print(df['date'][ind], df['precipitation'][ind])

    return jsonify(output)

@app.route("/api/v1.0/stations")
def stations():
    output = []
    station_count = session.query(measurement.station, func.count(measurement.station).label('frequency'))\
    .group_by(measurement.station)\
    .order_by(func.count(measurement.station).desc())\
    .all()

    for s in station_count:
        output.append(s['station'])

    return jsonify(output)

@app.route("/api/v1.0/tobs")
def tobs():

    output = []

    #Find the first day
    last_day = session.query(measurement.date).order_by(measurement.date.desc()).first()
    day_last_year = datetime.datetime.strptime(str(last_day[0]), '%Y-%m-%d') - datetime.timedelta(days=365)
    day_last_year_str = day_last_year.strftime('%Y-%m-%d')

    station_count = session.query(measurement.station, func.count(measurement.station).label('frequency'))\
    .group_by(measurement.station)\
    .order_by(func.count(measurement.station).desc())\
    .all()

    sel_data = session.query(measurement.station, measurement.date, measurement.prcp, measurement.tobs)\
    .filter(measurement.date >= day_last_year_str)\
    .filter(measurement.station == station_count[0]['station'])\
    .all()
    
    for r in sel_data:
        new_dict = {}
        new_dict['date'] = r['date']
        new_dict['station'] = r['station']
        new_dict['temperature'] = r['tobs']
        output.append(new_dict)

    return jsonify(output)

@app.route("/api/v1.0/<start>")
def start(start):

    output = {}

    if start:
        start = start.replace(' ','-').replace('/','-')

        sel_data = session.query(func.min(measurement.tobs),func.max(measurement.tobs),func.avg(measurement.tobs))\
        .filter(measurement.station == station.station)\
        .filter(measurement.date >= start)\
        .all()

        output['TMIN'] = sel_data[0][0]
        output['TMAX'] = sel_data[0][1]
        output['TAVG'] = sel_data[0][2]

    return jsonify(output)

@app.route("/api/v1.0/<start>/<end>")
def startend(start, end):

    output = {}

    if start and end:
        start = start.replace(' ','-').replace('/','-')
        end = end.replace(' ','-').replace('/','-')

        sel_data = session.query(func.min(measurement.tobs),func.max(measurement.tobs),func.avg(measurement.tobs))\
        .filter(measurement.station == station.station)\
        .filter(measurement.date >= start)\
        .filter(measurement.date <= end)\
        .all()

        output['TMIN'] = sel_data[0][0]
        output['TMAX'] = sel_data[0][1]
        output['TAVG'] = sel_data[0][2]

    return jsonify(output)

if __name__ == "__main__":
    app.run(debug=True)