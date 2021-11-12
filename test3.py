import json
import requests
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

caps = DesiredCapabilities.CHROME
caps['goog:loggingPrefs'] = {'performance': 'ALL'}
options = webdriver.ChromeOptions()
options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(desired_capabilities=caps,options=options)
driver.get('https://www.twitch.tv/amouranth')

# driver.find_element_by_id("play-button").click()


def process_browser_log_entry(entry):
    response = json.loads(entry['message'])['message']
    return response

while True:
    browser_log = driver.get_log('performance') 
    events = [process_browser_log_entry(entry) for entry in browser_log]
    events = [event for event in events if 'Network.response' in event['method']]

    # print(events)

    # val = json.dumps(events)
    # with open('txid.json','a') as f:
    #     f.write(val)

    # break

    for e in events:
        # print(e)
        try:
            url = e['params']['response']['url']
            if url.endswith('.ts'):
                print(e['params']['response']['status'])
                print(url)
                print('\n\n')
                # r1 = requests.get(url, stream=True)
                # if(r1.status_code == 200):
                #     with open('testvod.mpeg','ab') as f:
                #         for chunk in r1.iter_content(chunk_size=1024):
                #             f.write(chunk)
                # else:
                #     print("Received unexpected status code {}".format(r1.status_code))
        except KeyError as e:
            # print(e)
            pass

driver.quit()