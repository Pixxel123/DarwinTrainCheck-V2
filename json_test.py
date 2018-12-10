import requests
from darwin_token import DARWIN_KEY

jsonToken = DARWIN_KEY

train_station = {'work_station': 'whs', 'home_station': 'tth', 'connect_station': 'whs'}
user_time = {'morning_time': ['0821', '0853', '2147'], 'evening_time': ['1703', '1733'], 'connect_time': ['0834', '0843']}


def darwinChecker(departure_station, arrival_station, user_time):
    response = requests.get("https://huxley.apphb.com/all/" + str(departure_station) + "/to/" + str(arrival_station) + "/" + str(user_time), params={"accessToken": jsonToken})
    response.raise_for_status()    # this makes an error if something failed
    data1 = response.json()
    train_service = data1["trainServices"]
    # WHS -> TTH rsid: SN324200
    # print(type(train_service))
    print('Departure Station: ' + str(data1.get('crs')))
    print('Arrival Station: ' + str(data1.get('filtercrs')))
    print('-' * 30)
    # try:
    for index, service in enumerate(train_service):
        if service['sta'].replace(':', '') in user_time:  # replaces sta time with values in user_time
            print(type(train_service))
            print('Service ID: ' + str(train_service[index]['serviceID']))
            print('Service RSID: ' + str(train_service[index]['rsid']))
            print('Scheduled arrival time: ' + str(train_service[index]['sta']))
            print('Scheduled departure time: ' + str(train_service[index]['std']))
            print('Status: ' + str(train_service[index]['eta']))
            print('*' * 20)
        # for index, service in enumerate(train_service):
        if service['sta'] == '20:17':
            print(f'this is the first one {service["sta"]}')
        if service['rsid'] == 'SN063200':
            # this is the one we want to go back
            print(f'Previous sta check: {train_service[index-1]["sta"]}')
    # except TypeError:
        # print('There is no train service data')
    try:
        print('\nNRCC Messages: ' + str(data1['nrccMessages'][0]['value']))
    except TypeError:
        print('There is no NRCC data currently available\n')


# print('Morning Journey'.center(50, '='))
darwinChecker(train_station['home_station'], train_station['connect_station'], user_time['morning_time'])

# print('Connection Journey'.center(50, '='))
# darwinChecker(train_station['connect_station'], train_station['work_station'], user_time['connect_time'])

# print('Evening Journey'.center(50, '='))