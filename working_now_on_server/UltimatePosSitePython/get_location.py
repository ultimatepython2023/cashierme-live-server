from urllib.request import urlopen
import json




ip_address = '156.210.86.108';
url = 'https://api.ip2location.com/v2/?key=GHKTZJ965P&ip=' + ip_address+'&format=json&package=WS25&&addon=continent,country,region,city,geotargeting,country_groupings,time_zone_info&lang=zh-cn';
response = urlopen(url)
data = json.loads(response.read())
get_country_code = data['country']['alpha3_code']
get_country_name = data['country']['name']
print(get_country_code,
get_country_name)