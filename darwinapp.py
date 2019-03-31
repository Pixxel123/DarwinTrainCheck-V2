from flask import Flask
from flask import render_template
from flask import request
# from flask import jsonify
# import json
import requests
import re
import os
from types import SimpleNamespace
app = Flask(__name__)

# print('##########################################')
# print(SECRET_KEY)
# print(os.environ)
# print(os.environ.get('DARWIN_KEY', 'testing'))
SECRET_KEY = os.environ.get('DARWIN_KEY', None)
# print(SECRET_KEY)
# print('##########################################')
# jsonToken = DARWIN_KEY

mytrains = {}

# time_trains = {}

# time_of_day = 0

train_service_data = {}

train_station_data = {}

dest = 0
origin = 0
mytimes = 0
myurl = 0


@app.route("/")
@app.route("/home")
def hello():
    text = 'Flask is up and running!'
    return text


@app.route("/nametest", methods=["GET"])
def web_test():
    name = request.args.get('name')
    colours = request.args.get('colours')
    mytext = f"Hello, {name}. Your fave colour is {colours}."
    return mytext


@app.route("/gettrains", methods=["GET"])
def trains_test():
    origin = request.args.get('origin')
    dest = request.args.get('dest')
    mytimes = request.args.get('mytimes')
    myurl = f"http://huxley.apphb.com/all/{origin}/to/{dest}/{mytimes}?accessToken=" + SECRET_KEY
    return myurl


def checker():
    global mytrains  # modifies the global copy of mytrains otherwise a new variable is created
    global myurl
    global mytimes
    # myurl = f"http://huxley.apphb.com/all/{origin}/to/{dest}/{mytimes}"
    response = requests.get(myurl, params={"accessToken": SECRET_KEY})
    response.raise_for_status()  # this makes an error if something failed
    data1 = response.json()
    mytrains['departure'] = str(data1['crs'])
    mytrains['arrival'] = str(data1['filtercrs'])
    try:
        found_service = 0
        for index, service in enumerate(data1['trainServices']):  # indexes data for pulling of previous values
            if service['std'].replace(':', '') in mytimes:
                found_service += 1
                train = SimpleNamespace(
                    serviceID=str(service['serviceID']),
                    arrival_time=str(service['std']),
                    estimated_arrival=str(service['etd']),
                    status='On time'
                )
                prior_service = data1['trainServices'][index - 1]
                if train.estimated_arrival == 'Cancelled':
                    train.status = 'Cancelled'
                    train.alternate_service = str(prior_service['std'])
                    train.alternate_status = str(prior_service['etd'])
                elif train.estimated_arrival != 'On time':
                    train.status = 'Delayed'
                write_index = index
                for i, v in mytrains.items():
                    if isinstance(v, dict) and v['arrival_time'] == train.arrival_time:
                        write_index = i
                mytrains[write_index] = train.__dict__
            elif found_service == 0:  # if no service is found
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


def time_trains_services():  # splits data into train services lookup
    global train_service_data
    train_service_data = [j for i, j in mytrains.items() if isinstance(j, dict)]  # grabs train service data into dict
    return train_service_data


def time_trains_location():  # splits data into crs, filtercrs and nrcc queries
    global train_station_data
    train_station_data = {i: j for i, j in mytrains.items() if not isinstance(j, dict)}  # grabs [0] data into separate dict
    return train_station_data


@app.route("/getstatus", methods=["GET"])
def status_check():
    global myurl
    global mytimes
    global origin
    global dest
    origin = request.args.get('origin')
    dest = request.args.get('dest')
    mytimes = request.args.get('mytimes')
    myurl = f"http://huxley.apphb.com/all/{origin}/to/{dest}/{mytimes}"
    output = checker()
    return render_template('index.html', traindata=mytrains, trainstation=time_trains_location(), trainservices=time_trains_services())


if __name__ == '__main__':
    app.run()
