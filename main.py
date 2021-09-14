import requests
from bs4 import BeautifulSoup

link = "https://wolt.com/en/ltu/kaunas/restaurant/chick-n-roll"
# link = "https://wolt.com/en/ltu/kaunas/restaurant/ilunch-k-donelaicio-g"
r = requests.get(link)
soup = BeautifulSoup(r.content, 'html.parser')
delivery = soup.find('button', class_ = 'DeliveryTypeButton-module__root___c0B1z Venue-module__headerButton___3zfqF')
delivery = delivery.find('span', class_ = 'ContentButton-module__text___2PSlt')
if delivery.text == "Schedule for later":
    print("Not available")
else:
    print("Available")
