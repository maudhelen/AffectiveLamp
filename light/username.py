import requests

bridge_ip = "192.168.1.102"
url = f"http://{bridge_ip}/api"

data = {
    "devicetype": "my_app_name#maud"
}

response = requests.post(url, json=data)
print(response.json())