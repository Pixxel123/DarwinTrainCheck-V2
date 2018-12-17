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


print('Morning Journey'.center(50, '='))
darwinChecker(train_station['home_station'], train_station['connect_station'], user_time['morning_time'])

print('Connection Journey'.center(50, '='))
darwinChecker(train_station['connect_station'], train_station['work_station'], user_time['connect_time'])

# print('Evening Journey'.center(50, '='))
# darwinChecker(train_station['work_station'], train_station['home_station'], user_time['evening_time'])
