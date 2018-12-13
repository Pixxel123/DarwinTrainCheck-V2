import requests
import re
from darwin_token import DARWIN_KEY

jsonToken = DARWIN_KEY

train_station = {'work_station': 'whs', 'home_station': 'tth', 'connect_station': 'ecr'}
user_time = {'morning_time': ['0821', '0853'], 'evening_time': ['1733'], 'connect_time': ['0834', '0843']}


def darwinChecker(departure_station, arrival_station, user_time):
    response = requests.get("https://huxley.apphb.com/all/" + str(departure_station) + "/to/" + str(arrival_station) + "/" + str(user_time), params={"accessToken": jsonToken})
    response.raise_for_status()    # this makes an error if something failed
    data1 = response.json()
    train_service = data1["trainServices"]
    # WHS -> TTH rsid: SN324200
    # print(type(train_service))
    print('Departure Station: ' + str(data1.get('crs')))
    print('Arrival Station: ' + str(data1.get('filtercrs')))
    print('-' * 40)
    found_service = 0
    if found_service == 0:
            print('The services currently available are not specified in user_time.')
    try:
        for index, service in enumerate(train_service):
            if service['sta'].replace(':', '') in user_time:  # replaces sta time with values in user_time
                found_service += 1
                print('Service ID: ' + str(train_service[index]['serviceID']))
                print('Service RSID: ' + str(train_service[index]['rsid']))
                print('Scheduled arrival time: ' + str(train_service[index]['sta']))
                print('Scheduled departure time: ' + str(train_service[index]['std']))
                print('Status: ' + str(train_service[index]['eta']))
                print('-' * 40)
                print(found_service)
                if service['eta'] == 'Cancelled':
                    # print('The ' + str(train_service[index]['sta']) + ' service is cancelled.')
                    print('Previous train departure time: ' + str(train_service[index - 1]['sta']))
                    print('Previous train status: ' + str(train_service[index - 1]['eta']))
        return found_service
    except TypeError:
        print('There is no train service data')
    try:
        print('\nNRCC Messages: ' + str(data1['nrccMessages'][0]['value']))
        NRCCRegex = re.compile('^(.*?)[\.!\?](?:\s|$)')  # regex pulls all characters until hitting a . or ! or ?
        myline = NRCCRegex.search(data1['nrccMessages'][0]['value'])  # regex searches through nrccMessages
        print('\nNRCC Messages: ' + myline.group(1))  # prints parsed NRCC message
    except TypeError:
        print('There is no NRCC data currently available\n')


print('Morning Journey'.center(50, '='))
darwinChecker(train_station['home_station'], train_station['connect_station'], user_time['morning_time'])

# print('Connection Journey'.center(50, '='))
# darwinChecker(train_station['connect_station'], train_station['work_station'], user_time['connect_time'])

# print('Evening Journey'.center(50, '='))
# darwinChecker(train_station['work_station'], train_station['home_station'], user_time['evening_time'])
