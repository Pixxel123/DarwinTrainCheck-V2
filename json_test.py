import json
from urllib.request import urlopen
from darwin_token import DARWIN_KEY

jsonToken = DARWIN_KEY
dep_station = 'whs'
arr_station = 'tth'

time1 = ('1653,1733')

userTime = ['1703','1733']

try:
    with urlopen("https://huxley.apphb.com/all/" + dep_station + "/to/" + arr_station + "/" + str(time1) + "?accessToken=" + jsonToken) as response:
        source1 = response.read().decode('utf-8')
    data1 = json.loads(source1)  # TTH -> ECR journey loaded as dict

    # with urlopen("https://huxley.apphb.com/dep/ecr/to/whs?accessToken=" + jsonToken) as response:
        # source2 = response.read().decode('utf-8')
    # data2 = json.loads(source2)  # ECR -> WHS journey
except urllib.error.URLError as e:
    ResponseData = e.reason
    print('No data connection')
# WHS -> TTH rsid: SN324200
# TODO: Use rsid value to return same journey information
# print(json.dumps(data1, indent=2))


print('Departure Station: ' + str(data1.get('crs')))
print('Arrival Station: ' + str(data1.get('filtercrs')))
print('-' * 30)

try:
    for i in range(0, len(data1['trainServices'])):
        if data1['trainServices'][i]['sta'].replace(':', '') in userTime:  # replaces sta time with values in userTime
            print('Service ID: ' + str(data1['trainServices'][i]['serviceID']))
            print('Service RSID: ' + str(data1['trainServices'][i]['rsid']))
            print('Scheduled arrival time: ' + str(data1['trainServices'][i]['sta']))
            print('Actual arrival: ' + str(data1['trainServices'][i]['eta']))
            print()
        # if data1['trainServices'][i]['etd'] == 'On time':
        #     print('')
        # else:
        #     print('Status: ' + str(data1['trainServices'][i]['etd']))
        # print('Status: ' + str(data1['trainServices'][i]['etd']))
        # print(data1['trainServices'][i]['origin'])
except TypeError:
    print('There is no train service data')
try:
    print('\nNRCC Messages: ' + str(data1['nrccMessages'][0]['value']))
except TypeError:
    print('There is no NRCC data currently available')

# origin is a list, not a dict
# for item in data1:
    # for data_item in item['data1']:
        # print(data_item['rsid'])

# user_risd = 'SN326500'

