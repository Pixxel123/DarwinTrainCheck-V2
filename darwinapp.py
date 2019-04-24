from flask import Flask
from flask import render_template
from flask import request
import requests
import os
from types import SimpleNamespace

app = Flask(__name__)

SECRET_KEY = os.environ.get('DARWIN_KEY', None)
# SECRET_KEY = '4245c8a6-8a88-4727-9f99-29875e6914b4'

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


def get_services():
    train_services = url_parameters()  # name the returned tuple, train_services[0] = full_data, train_services[1] = mytimes
    service_times = {}  # initialises empty dict
    for index, service in enumerate(train_services[0]['trainServices']):  # looks through the trainServices json, indexes values for later lookup
        service_info = train_services[1]  # renames mytimes variable
        if service['std'].replace(':', '') in service_info:  # looks for 'std' key in json, if matches service_info
            train = SimpleNamespace(  # initialises train namespace
                serviceID=str(service['serviceID']),  # serviceID info
                arrival_time=str(service['std']),  # scheduled departure info
                estimated_arrival=str(service['etd']),  # estimated departure time
                status='On time')  # service status
            prior_service = train_services[0]['trainServices'][index - 1]  # grabs previous indexed data
            if train.estimated_arrival == 'Cancelled':
                train.status = 'Cancelled'
                train.alternate_service = str(prior_service['std'])  # scheduled departure of previous service
                train.alternate_status = str(prior_service['etd'])  # estimated departure of previous service
            elif train.estimated_arrival != 'On time':  # if train arrival not on time
                train.status = 'Delayed'  # set status to Delayed
            write_index = index
            for items, values in service_times.items():
                if isinstance(values, dict) and values['arrival_time'] == train.arrival_time:
                    write_index = items
            service_times[write_index] = train.__dict__
    return service_times


@app.route("/getstatus", methods=["GET"])
def main_page():
    service_info = get_services()
    return render_template('trainspage.html', trainservice=service_info)


if __name__ == '__main__':
    app.run()
