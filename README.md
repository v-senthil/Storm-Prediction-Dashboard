# Storm-Prediction-Dashboard

## Software Used:
1. Python - Flask Web Framework (Backend)
2. HTML and CSS (Front End)
3. Plotly (Visualization)
4. Fema API
5. Twilio (Message Service)

## Working:
1. Download this repository
2. Static folder contains all the CSS, JS, Images and Uploads.
3. Template folder contains all the HTML pages.
4. App.py is the main file.
5. Run
"pip install requirements.txt"
Which will install all the required libraries
6. Run the app
"Python app.py"
7. There are 4 kinds of filtering present
- By State
- By State and Date
- By Date and Disaster Type
- By State, Date and Disaster Type
8. Every time you give the input, the app calls the respective API and gets a
JSON response.
9. This JSON response is converted into a pandas dataframe.
10. From which FIPS code is obtained.
11. FIPS code is then used to visualize the data affected using choropleth
map.

## Features:
1. If the incident date is equal to the current date, it will directly give the user
and notification via a message.
2. File Upload - If any file is to be uploaded to the server for any future
reference, it can be done.
3. Fema Database can be downloaded right from the app as a CSV format,
which can be used for Tableau and PowerBI.
4. Message service using Twilio.
