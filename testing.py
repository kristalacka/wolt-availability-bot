import requests

link = "https://restaurant-api.wolt.com/v3/venues/slug/chick-n-roll"
r = requests.get(link)
status = r.json().get("results", {})[0].get("alive")
if status:
    print("available")
