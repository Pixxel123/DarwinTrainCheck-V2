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
user_time = {'morning_time': ['1021', '1049'], 'evening_time': ['1433', '1723'], 'connect_time': ['0817', '0825']}

mytrains = {}
# def url_request(departure_station, arrival_station, user_time):
#     url = "https://huxley.apphb.com/all/" + str(departure_station) + "/to/" + str(arrival_station) + "/" + str(user_time), params={"accessToken": jsonToken}
#     return url


@app.route("/")
@app.route("/home")
def hello():
    formed_string = '<p>Thing: ' + 'One</p>' + '\n'
    formed_string += '<p>Thing: ' + 'Two</p>' + '\n'
    formed_string += '<p>Thing: ' + 'Three</p>' + '\n'
    text = formed_string.replace('\n', '<br/>')
    return text


def darwinChecker(departure_station, arrival_station, user_time):
    response = requests.get("https://huxley.apphb.com/all/" + str(departure_station) + "/to/" + str(arrival_station) + "/" + str(user_time), params={"accessToken": jsonToken})
    response.raise_for_status()    # this makes an error if something failed
    data1 = response.json()
    train_service = data1["trainServices"]
    print('Departure Station: ' + str(data1['crs']))
    print('Arrival Station: ' + str(data1['filtercrs']))
    print('-' * 40)
    try:
        found_service = 0  # keeps track of services so note is generated if service not in user_time
        for index, service in enumerate(train_service):  # enumerate adds index value to train_service list
            if service['sta'].replace(':', '') in user_time:  # replaces sta time with values in user_time
                found_service += 1  # increments for each service in user_time
                print('Service RSID: ' + str(train_service[index]['rsid']))
                print('Scheduled arrival time: ' + str(train_service[index]['sta']))
                print('Scheduled departure time: ' + str(train_service[index]['std']))
                print('Status: ' + str(train_service[index]['eta']))
                print('-' * 40)
                if service['eta'] == 'Cancelled':
                    print('The ' + str(train_service[index]['sta']) + ' service is cancelled.')
                    print('Previous train departure time: ' + str(train_service[index - 1]['sta']))
                    print('Previous train status: ' + str(train_service[index - 1]['eta']))
        if found_service == 0:  # if no service is found
            print('The services currently available are not specified in user_time.')
    except TypeError:
        print('There is no train service data')
    try:
        NRCCRegex = re.compile('^(.*?)[\.!\?](?:\s|$)')  # regex pulls all characters until hitting a . or ! or ?
        myline = NRCCRegex.search(data1['nrccMessages'][0]['value'])  # regex searches through nrccMessages
        print('\nNRCC Messages: ' + myline.group(1) + '\n')  # prints parsed NRCC message
    except (TypeError, AttributeError) as error:  # tuple catches multiple errors, AttributeError for None value
        print('\nThere is no NRCC data currently available\n')


def darwin_checker_dict(departure_station, arrival_station, user_time):
    response = requests.get("https://huxley.apphb.com/all/" + str(departure_station) + "/to/" + str(arrival_station) + "/" + str(user_time) + '?', params={"accessToken": SECRET_KEY})
    response.raise_for_status()  # this makes an error if something failed
    data1 = response.json()
    mytrains['departure'] = str(data1['crs'])
    mytrains['arrival'] = str(data1['filtercrs'])
    # try:
    found_service = 0
    for index, service in enumerate(data1['trainServices']):
        if service['sta'].replace(':', '') in user_time:
            found_service += 1
            mytrains['rsid'] = str(data1['trainServices'][index]['rsid'])
            mytrains['arrival_time'] = str(data1['trainServices'][index]['sta'])
            mytrains['estimated_arrival'] = str(data1['trainServices'][index]['eta'])
            if mytrains['estimated_arrival'] == 'On time':
                mytrains['status'] = 'On time'
            if mytrains['estimated_arrival'] != 'On time':
                mytrains['status'] = 'Delayed'
            if service['eta'] == 'Cancelled':
                mytrains['status'] = 'Cancelled'
                mytrains['alternate_service'] = str(data1['trainServices'][index - 1]['sta'])
                mytrains['alternate_status'] = str(data1['trainServices'][index - 1]['eta'])
    # if found_service == 0:  # if no service is found
        # mytrains['state'] = 'The services currently available are not specified in user_time.'
# except TypeError:
    # mytrains['errorMessage'] = 'There is no train service data'
    try:
        NRCCRegex = re.compile('^(.*?)[\.!\?](?:\s|$)')  # regex pulls all characters until hitting a . or ! or ?
        myline = NRCCRegex.search(data1['nrccMessages'][0]['value'])  # regex searches through nrccMessages
        mytrains['nrcc'] = myline.group(1)  # prints parsed NRCC message
    except (TypeError, AttributeError) as error:  # tuple catches multiple errors, AttributeError for None value
        mytrains['nrcc'] = 'There is no NRCC data currently available'
        return mytrains


@app.route('/morning')
def darwin_morning():
    darwin_checker_dict(train_station['home_station'], train_station['connect_station'], user_time['morning_time'])
    return render_template('index.html', traindata=mytrains)


@app.route('/connection')
def darwin_connect():
    darwin_checker_dict(train_station['connect_station'], train_station['work_station'], user_time['connect_time'])
    return render_template('index.html', traindata=mytrains)


@app.route('/evening')
def darwin_evening():
    darwin_checker_dict(train_station['work_station'], train_station['connect_station'], user_time['evening_time'])
    return render_template('index.html', traindata=mytrains)


if __name__ == '__main__':
    app.run()
