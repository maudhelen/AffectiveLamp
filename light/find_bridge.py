import requests
response = requests.get("https://discovery.meethue.com/")
print(response.json())