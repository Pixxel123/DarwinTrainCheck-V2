from flask import Flask
from flask import render_template
# from flask import jsonify
# import json
import requests
import re
import os
app = Flask(__name__)

print('##########################################')
# print(SECRET_KEY)
print(os.environ)
print(os.environ.get('DARWIN_KEY', 'testing'))
SECRET_KEY = os.environ.get('DARWIN_KEY', None)
print(SECRET_KEY)
print('##########################################')
# jsonToken = DARWIN_KEY

train_station = {'work_station': 'whs', 'home_station': 'orp', 'connect_station': 'lbg'}
user_time = {'morning_time': ['1241'], 'evening_time': ['1333', '1353'], 'connect_time': ['0817', '0825']}

mytrains = {}

time_trains = {}

time_of_day = 0


@app.route("/")
@app.route("/home")
def hello():
    formed_string = '<p>Thing: ' + 'One</p>' + '\n'
    formed_string += '<p>Thing: ' + 'Two</p>' + '\n'
    formed_string += '<p>Thing: ' + 'Three</p>' + '\n'
    text = formed_string.replace('\n', '<br/>')
    return text


def darwin_checker(departure_station, arrival_station, query_time):
    # global mytrains  # modifies the global copy of mytrains otherwise a new variable is created
    formatted_times = ",".join(query_time)
    response = requests.get("https://huxley.apphb.com/all/" + str(departure_station) + "/to/" + str(arrival_station) + "/" + str(formatted_times), params={"accessToken": SECRET_KEY})
    response.raise_for_status()  # this makes an error if something failed
    data1 = response.json()
    mytrains['departure'] = str(data1['crs'])
    mytrains['arrival'] = str(data1['filtercrs'])
    try:
        found_service = 0
        for index, service in enumerate(data1['trainServices']):
            if service['std'].replace(':', '') in formatted_times:
                found_service += 1
                mytrains[index] = {}
                mytrains[index]['serviceID'] = str(data1['trainServices'][index]['serviceID'])
                mytrains[index]['arrival_time'] = str(data1['trainServices'][index]['std'])
                mytrains[index]['estimated_arrival'] = str(data1['trainServices'][index]['eta'])
                if mytrains[index]['estimated_arrival'] == 'On time':
                    mytrains[index]['status'] = 'On time'
                if mytrains[index]['estimated_arrival'] != 'On time':
                    mytrains[index]['status'] = 'Delayed'
                if mytrains[index]['estimated_arrival'] == 'Cancelled':
                    mytrains[index]['status'] = 'Cancelled'
                    mytrains[index]['alternate_service'] = str(data1['trainServices'][index - 1]['std'])
                    mytrains[index]['alternate_status'] = str(data1['trainServices'][index - 1]['eta'])
                new = {}
                new['serviceID'] = str(data1['trainServices'][index]['serviceID'])
                new['arrival_time'] = str(data1['trainServices'][index]['std'])
                new['estimated_arrival'] = str(data1['trainServices'][index]['eta'])
                if new['estimated_arrival'] == 'On time':
                    new['status'] = 'On time'
                if new['estimated_arrival'] != 'On time':
                    new['status'] = 'Delayed'
                if new['estimated_arrival'] == 'Cancelled':
                    new['status'] = 'Cancelled'
                    new['alternate_service'] = str(data1['trainServices'][index - 1]['std'])
                    new['alternate_status'] = str(data1['trainServices'][index - 1]['eta'])
                if all([mytrains[i] != new for i in mytrains]):
                    mytrains[index] = new
        if found_service == 0:  # if no service is found
            mytrains['state'] = 'The services currently available are not specified in user_time.'
    except (TypeError, AttributeError) as error:
        mytrains['errorMessage'] = 'There is no train service data'
    try:
        NRCCRegex = re.compile('^(.*?)[\.!\?](?:\s|$)')  # regex pulls all characters until hitting a . or ! or ?
        myline = NRCCRegex.search(data1['nrccMessages'][0]['value'])  # regex searches through nrccMessages
        mytrains['nrcc'] = myline.group(1)  # prints parsed NRCC message
    except (TypeError, AttributeError) as error:  # tuple catches multiple errors, AttributeError for None value
        mytrains['nrcc'] = 'No NRCC'
    return mytrains


def darwin_time(time_of_day):
    global time_trains
    # global sorted_trains
    time_trains = darwin_checker(train_station['work_station'], train_station['connect_station'], user_time[time_of_day])
    # sorted_trains = [train for i, train in time_trains.items() if isinstance(train, dict)]
    return time_trains


def time_trains_services():
    train_service_data = [j for i, j in time_trains.items() if isinstance(j, dict)]  # grabs train service data into dict
    return train_service_data


def time_trains_location():
    train_station_data = {i: j for i, j in time_trains.items() if not isinstance(j, dict)}  # grabs [0] data into separate dict
    return train_station_data


@app.route('/second')
def page():
    darwin_time('evening_time')
    return render_template('index.html', traindata=darwin_time('evening_time'), trainstation=time_trains_location(), trainservices=time_trains_services())


if __name__ == '__main__':
    app.run()
