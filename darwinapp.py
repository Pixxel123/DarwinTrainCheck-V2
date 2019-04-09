from flask import Flask
from flask import render_template
from flask import request
import requests
import re
import os
from types import SimpleNamespace

app = Flask(__name__)

SECRET_KEY = os.environ.get('DARWIN_KEY', None)

# test page to show that Flask is up and running


@app.route('/')
@app.route('/home')
def home_page():
    string = 'Hello World! Flask is running!'
    return string


def url_parameters():  # defines lookup parameters in URL
    origin = request.args.get('origin')  # origin station
    dest = request.args.get('dest')  # destination station
    mytimes = request.args.get('mytimes')  # times to lookup
    check_url = f"http://huxley.apphb.com/all/{origin}/to/{dest}/{mytimes}"  # format URL for API lookup
    response = requests.get(check_url, params={"accessToken": SECRET_KEY})  # get URL and make request, with API key
    response.raise_for_status()  # raises the relevant error if status code is not 200
    full_data = response.json()  # url data as a json is given name 'full_data'
    return full_data, mytimes  # output tuple, url_parameters()[0] = full_data, url_parameters()[1] = mytimes


def get_location():  # grabs stations data and NRCC messages
    trains_location = url_parameters()  # assigns url to variable
    for full_data in url_parameters()[0]:  # loops through full_data from url_parameters()
        trains_location = {}  # empty dict is initialised
        trains_location['departure'] = url_parameters()[0]['crs']
        trains_location['arrival'] = url_parameters()[0]['filtercrs']
        trains_location['generated'] = url_parameters()[0]['generatedAt']
        try:
            NRCCRegex = re.compile('^(.*?)[\.!\?](?:\s|$)')  # regex pulls all characters until hitting a . or ! or ?
            myline = NRCCRegex.search(url_parameters()[0]['nrccMessages'][0]['value'])  # regex searches through nrccMessages
            trains_location['nrcc'] = myline.group(1)  # prints parsed NRCC message
        except (TypeError, AttributeError) as error:  # tuple catches multiple errors, AttributeError for None value
            trains_location['nrcc'] = 'No NRCC'
    return trains_location


def get_services():
    train_services = url_parameters()  # name the returned tuple, train_services[0] = full_data, train_services[1] = mytimes
    found_service = 0
    service_times = {}
    for index, service in enumerate(train_services[0]['trainServices']):
        service_info = train_services[1]
        if service['std'].replace(':', '') in service_info:
            found_service += 1
            train = SimpleNamespace(
                serviceID=str(service['serviceID']),
                arrival_time=str(service['std']),
                estimated_arrival=str(service['etd']),
                status='On time')
            prior_service = train_services[0]['trainServices'][index - 1]
            if train.estimated_arrival == 'Cancelled':
                train.status = 'Cancelled'
                train.alternate_service = str(prior_service['std'])
                train.alternate_status = str(prior_service['etd'])
            elif train.estimated_arrival != 'On time':
                train.status = 'Delayed'
            write_index = index
            for items, values in service_times.items():
                if isinstance(values, dict) and values['arrival_time'] == train.arrival_time:
                    write_index = items
            service_times[write_index] = train.__dict__
    return service_times


@app.route("/getstatus", methods=["GET"])
def main_page():
    return render_template('test.html', traindata=url_parameters(), location_data=get_location(), trainservice=get_services())


if __name__ == '__main__':
    app.run()
