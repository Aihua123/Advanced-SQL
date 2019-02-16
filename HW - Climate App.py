import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import requests

# global scrope
def get_session(table_required=None):
    engine = create_engine("sqlite:///hawaii.sqlite")
    Base = automap_base()
    Base.prepare(engine, reflect=True)
    #Table = Base.table_required
    Measurement = Base.classes.measurement
    Station = Base.classes.station
    session = Session(engine)
    #return (session, Table)
    return (session, Measurement, Station)


app = Flask(__name__)

@app.route("/")
def home():
    return(
        f"""Available Routes: 
        /api/v1.0/precipitation, 
        /api/v1.0/stations, 
        /api/v1.0/tobs, 
        /api/v1.0/start_date
        /api/v1.0/start_date/end_date""")
    
@app.route("/api/v1.0/precipitation")
def get_prcp():
    dictionary = []
    session, Measurement, _ = get_session() #function returns 3 variables we need to use
    for row in session.query(Measurement).all():
        dictionary.append({'Date': row.date,'Precipitation': row.prcp})
    return jsonify(dictionary)

@app.route("/api/v1.0/stations")
def get_stations():
    session, _, Station = get_session()
    stations = session.query(Station.station).all()
    return jsonify(stations)
    
@app.route("/api/v1.0/tobs")
def get_temp_last_year():
    result = []
    session, Measurement, _ = get_session()
    for row in session.query(Measurement.date,Measurement.tobs).filter(Measurement.date >= '2016-08-18').all():
        result.append({'Date': row[0],'Temperature': row[1]})
    return jsonify(result)

@app.route("/api/v1.0/<start_date>")
def get_calc_temp(start_date):
    session, Measurement, _ = get_session()
    for date in session.query(Measurement.date).order_by(Measurement.date).first():
        f_date = date
    for date in session.query(Measurement.date).order_by(Measurement.date.desc()).first():
        l_date = date
    res = []
    if start_date < f_date or start_date > l_date:
        return f"Sorry, temperature for the requested dates is not available. Please request data between {f_date} and {l_date}."
    else:
        for row in session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all():
            res.append({'Minimum Temp':row[0],'Average Temp': row[1],'Maximum Temp':row[2]})
        return jsonify(res)

@app.route("/api/v1.0/<start_date>/<end_date>")
# if start_date doesn't match some regexp, return "error, see docs about hwo to use start_date"
# import re
# outcome = re.findall('\d\d\d\d\-\d\d\-\d\d', start_date)
# if not outcome:   return "please use dates in the format yyyy-mm-dd"
def get_calc_temp_1(start_date,end_date):
    session, Measurement, _ = get_session()
    for date in session.query(Measurement.date).order_by(Measurement.date).first():
        f_date = date
    for date in session.query(Measurement.date).order_by(Measurement.date.desc()).first():
        l_date = date
    res = []
    if start_date < f_date or end_date > l_date:
        return f"Sorry, temperature for the requested dates is not available. Please request data between {f_date} and {l_date}."
    else:
        for row in session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all():
            res.append({'Minimum Temp':row[0],'Average Temp': row[1],'Maximum Temp':row[2]})
        return jsonify(res)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
