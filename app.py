import os
from werkzeug.utils import secure_filename
from flask import Flask,render_template, request, make_response, Response, redirect, url_for
from flask_mail import Mail, Message
import requests
from urllib.request import urlopen
import json
import pandas as pd
import plotly.express as px
import urllib3
import certifi
from twilio.rest import Client
import urllib.request
from datetime import date
from plyer import notification


app = Flask(__name__)

today = date.today()
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#Normal Message Function
def appmsg(number,message):
    account_sid = 'ACb2d596698148db142b89d7cb8666c147'
    auth_token = 'b89c7902694fd70fc25a788f6746502f'
    client = Client(account_sid, auth_token)
    message = client.messages \
        .create(
            from_='+12563339136',
            body=message,
            to=number
        )
    if message:
        return True
    else:
        return False

#State and Date
@app.route("/")
def index():
    return render_template('dashboard.html')

@app.route("/getapi", methods=['GET', 'POST'])
def getapi():

    #Get Date and State from HTML
    state = request.form['state']
    date = request.form['date']

    #US Dataset - GeoJSON
    with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
        counties = json.load(response)

    #Call FEMA API
    url = "https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries?$filter=incidentType%20eq%20%27Severe%20Storm(s)%27%20and%20incidentBeginDate%20gt%20%27"+date+"T04:00:00.000z%27%20and%20state%20eq%20%27"+state+"%27"
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',ca_certs=certifi.where())
    r = http.request('GET', url)
    femaapi = r.status
    if femaapi == 503:
        error = "FEMA.gov is experiencing technical difficulties - Response Code:503"
        return render_template("dashboard.html", error = error)
    else:
        data = json.loads(r.data.decode('utf-8'))

        #Check if Response is present in the JSON
        if data['DisasterDeclarationsSummaries'] == []:
            error = "No Data Avaliable in this Time Period for the state "+state
            return render_template('dashboard.html', error=error)
        else:

            # JSON to Dataframe
            df = pd.json_normalize(data, 'DisasterDeclarationsSummaries')

            #Create FIPS value according to the state in the dataframe
            df['fips'] = df['fipsStateCode']+df['fipsCountyCode']
            df['values'] = 1

            #Slice the declarationDate to get only the date
            df['incidentdate'] = df.declarationDate.str[:10]

            #If todays date is equal to incident date -> send message 
            for date in df['incidentdate']:
                if date == today:
                    notification.notify(title="Message form Fema API", message=f"Upcoming Strom Today - {today}",timeout=2)
                    number = '+919481119745'
                    message = "Declaration of Storm"
                    account_sid = 'ACb2d596698148db142b89d7cb8666c147'
                    auth_token = 'b89c7902694fd70fc25a788f6746502f'
                    client = Client(account_sid, auth_token)
                    message = client.messages \
                        .create(
                                from_='+12563339136',
                                body=message,
                                to=number
                        )

            #Plot map
            fig = px.choropleth_mapbox(df, geojson=counties, locations='fips',
                                color_continuous_scale="Viridis",
                                range_color=(0, 12),
                                mapbox_style="open-street-map",
                                zoom=3.5, center = {"lat": 37.0902, "lon": -95.7129},
                                opacity=0.5,
                                hover_name = df['designatedArea'],
                                hover_data=["state","incidentdate", "declarationTitle", "lastRefresh"]
                                )
            fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            fig.write_html("templates\\map.html")
            success = "Data obtained Sucessfully for the state - "+state
            return render_template('dashboard.html', success=success)

@app.route("/map")
def map():
    return render_template('map.html')    


#State
@app.route("/state")
def state():
    return render_template("state.html")


@app.route("/stateapi", methods=['POST', 'GET'])
def stateapi():
    state = request.form['state']

    with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
        counties = json.load(response)

    #Call FEMA API
    url = "https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries?$filter=incidentType%20eq%20%27Severe%20Storm(s)%27%20and%20state%20eq%20%27"+state+"%27"
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',ca_certs=certifi.where())
    r = http.request('GET', url)
    femaapi = r.status
    if femaapi == 503:
        error = "FEMA.gov is experiencing technical difficulties - Response Code:503"
        return render_template("state.html", error = error)
    else:
        data = json.loads(r.data.decode('utf-8'))

        #Check if Response is present in the JSON
        if data['DisasterDeclarationsSummaries'] == []:
            error = "No Data Avaliable in this Time Period for the state "+state
            return render_template('dashboard.html', error=error)
        else:

            # JSON to Dataframe
            df = pd.json_normalize(data, 'DisasterDeclarationsSummaries')

            #Create FIPS value according to the state in the dataframe
            df['fips'] = df['fipsStateCode']+df['fipsCountyCode']
            df['values'] = 1

            #Slice the declarationDate to get only the date
            df['incidentdate'] = df.declarationDate.str[:10]

            #If todays date is equal to incident date -> send message 
            for date in df['incidentdate']:
                if date == today:
                    notification.notify(title="Message form Fema API", message=f"Upcoming Strom Today - {today}",timeout=2)
                    number = '+919481119745'
                    message = "Declaration of Storm"
                    account_sid = 'ACb2d596698148db142b89d7cb8666c147'
                    auth_token = 'b89c7902694fd70fc25a788f6746502f'
                    client = Client(account_sid, auth_token)
                    message = client.messages \
                        .create(
                                from_='+12563339136',
                                body=message,
                                to=number
                        )

            #Plot map
            fig = px.choropleth_mapbox(df, geojson=counties, locations='fips',
                                color_continuous_scale="Viridis",
                                range_color=(0, 12),
                                mapbox_style="open-street-map",
                                zoom=3.5, center = {"lat": 37.0902, "lon": -95.7129},
                                opacity=0.5,
                                hover_name = df['designatedArea'],
                                hover_data=["incidentType","incidentdate", "declarationTitle", "lastRefresh"]
                                )
            fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            fig.write_html("templates\\statemap.html")
            success = "Data obtained Sucessfully for the state - "+state
            return render_template('state.html', success=success)

@app.route("/statemap")
def statemap():
    return render_template("statemap.html")


#Disaster and Date
@app.route("/disaster")
def disaster():
    return render_template("disaster.html")

@app.route("/disasterapi", methods=['POST', 'GET'])
def disasterapi():

    disaster = request.form['disaster']
    date = request.form['date']

    #US Dataset - GeoJSON
    with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
        counties = json.load(response)

    #Call FEMA API
    url = "https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries?$filter=incidentType%20eq%20%27"+disaster+"%27%20and%20incidentBeginDate%20gt%20%27"+date+"T04:00:00.000z%27%20"
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',ca_certs=certifi.where())
    r = http.request('GET', url)
    femaapi = r.status
    if femaapi == 503:
        error = "FEMA.gov is experiencing technical difficulties - Response Code:503"
        return render_template("disaster.html", error = error)
    else:
        data = json.loads(r.data.decode('utf-8'))

        #Check if Response is present in the JSON
        if data['DisasterDeclarationsSummaries'] == []:
            error = "No Data Avaliable in this Time Period for the Disaster "+disaster+ " or the API is not updated yet!"
            return render_template('disaster.html', error=error)
        else:

            # JSON to Dataframe
            df = pd.json_normalize(data, 'DisasterDeclarationsSummaries')

            #Create FIPS value according to the state in the dataframe
            df['fips'] = df['fipsStateCode']+df['fipsCountyCode']
            df['values'] = 1

            #Slice the declarationDate to get only the date
            df['incidentdate'] = df.declarationDate.str[:10]

            #If todays date is equal to incident date -> send message 
            for date in df['incidentdate']:
                if today == date:
                    notification.notify(title="Message form Fema API", message=f"Upcoming Strom Today - {today}",timeout=2)
                    number = '+919481119745'
                    message = "Declaration of Storm"
                    account_sid = 'ACb2d596698148db142b89d7cb8666c147'
                    auth_token = 'b89c7902694fd70fc25a788f6746502f'
                    client = Client(account_sid, auth_token)
                    message = client.messages \
                        .create(
                                from_='+12563339136',
                                body=message,
                                to=number
                        )

            #Plot map
            fig = px.choropleth_mapbox(df, geojson=counties, locations='fips',
                                color_continuous_scale="Viridis",
                                range_color=(0, 12),
                                mapbox_style="open-street-map",
                                zoom=3.5, center = {"lat": 37.0902, "lon": -95.7129},
                                opacity=0.5,
                                hover_name = df['state'],
                                hover_data=["designatedArea", "incidentdate", "declarationTitle", "lastRefresh"]
                                )
            fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            fig.write_html("templates\\disastermap.html")
            success = "Data obtained Sucessfully for the disaster - "+ disaster
            return render_template('disaster.html', success=success)

@app.route("/disastermap")
def disastermap():
    return render_template("disastermap.html")


#State, Disaster and Date
@app.route("/allapi")
def allapi():
    return render_template("allapi.html")

@app.route("/allapimap", methods=['POST', 'GET'])
def allapimap():

    state = request.form['state']
    disaster = request.form['disaster']
    date = request.form['date']

    #US Dataset - GeoJSON
    with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
        counties = json.load(response)

    #Call FEMA API
    url = "https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries?$filter=incidentType%20eq%20%27"+disaster+"%27%20and%20incidentBeginDate%20gt%20%27"+date+"T04:00:00.000z%27%20and%20state%20eq%20%27"+state+"%27"
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',ca_certs=certifi.where())
    r = http.request('GET', url)
    femaapi = r.status
    if femaapi == 503:
        error = "FEMA.gov is experiencing technical difficulties - Response Code:503"
        return render_template("allapi.html", error = error)
    else:
        data = json.loads(r.data.decode('utf-8'))

        #Check if Response is present in the JSON
        if data['DisasterDeclarationsSummaries'] == []:
            error = "No Data Avaliable in this Time Period for the Disaster "+disaster+" for the state "+state
            return render_template('allapi.html', error=error)
        else:

            # JSON to Dataframe
            df = pd.json_normalize(data, 'DisasterDeclarationsSummaries')

            #Create FIPS value according to the state in the dataframe
            df['fips'] = df['fipsStateCode']+df['fipsCountyCode']
            df['values'] = 1

            #Slice the declarationDate to get only the date
            df['incidentdate'] = df.declarationDate.str[:10]

            #If todays date is equal to incident date -> send message 
            for date in df['incidentdate']:
                if today == date:
                    notification.notify(title="Message form Fema API", message=f"Upcoming Strom Today - {today}",timeout=2)
                    number = '+919481119745'
                    message = "Declaration of Storm"
                    account_sid = 'ACb2d596698148db142b89d7cb8666c147'
                    auth_token = 'b89c7902694fd70fc25a788f6746502f'
                    client = Client(account_sid, auth_token)
                    message = client.messages \
                        .create(
                                from_='+12563339136',
                                body=message,
                                to=number
                        )

            #Plot map
            fig = px.choropleth_mapbox(df, geojson=counties, locations='fips',
                                color_continuous_scale="Viridis",
                                range_color=(0, 12),
                                mapbox_style="open-street-map",
                                zoom=3.5, center = {"lat": 37.0902, "lon": -95.7129},
                                opacity=0.5,
                                hover_name = df['designatedArea'],
                                hover_data=["incidentType", "incidentdate", "declarationTitle", "lastRefresh", "designatedArea"]
                                )
            fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            fig.write_html("templates\\allmap.html")
            success = "Data obtained Sucessfully for the disaster - "+ disaster+" at the State "+state
            return render_template('allapi.html', success=success)

@app.route("/allmap")
def allmap():
    return render_template("allmap.html")


#Notification Page
@app.route("/notify")
def notify():
    return render_template("notify.html")



#Error Handling
@app.errorhandler(404)
def error(error):
    return render_template("error.html"), 404


# Messaging Service
@app.route("/wamsg", methods=['POST'])
def wamsg():
    number = request.form['wa-phone']
    message = request.form['wa-msg']
    wa_msg = appmsg(number, message)
    if wa_msg:
        wa_error = 'Succesfull'
        return render_template('notify.html', wa_error=wa_error)

    else:
        wa_error = 'Invalid Credentials. Please try again.'
        return render_template('notify.html', wa_error=wa_error)


#Upload Page
@app.route("/upload")
def upload():
    return render_template("upload.html")

@app.route("/uploadfile", methods=['GET', 'POST'])
def uploadfile():
        if request.method == 'POST':
            file = request.files['file']
            filename = secure_filename(file.filename)
            upload = file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file_success = "Uploaded Succesfully"
            return render_template("upload.html", file_success=file_success)

#Download Fema Database as CSV File
@app.route("/getcsv")
def getPlotCSV():
    with open("static/docs/DisasterDeclarationsSummaries.csv") as fp:
        csv = fp.read()
    return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-disposition":
                 "attachment; filename=FEMA-DB.csv"})


if __name__ == "__main__":
    app.run(debug=True)