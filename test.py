import json
import requests
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

caps = DesiredCapabilities.CHROME
caps['goog:loggingPrefs'] = {'performance': 'ALL'}
options = webdriver.ChromeOptions()
options.add_argument("--window-size=1920,1080")
options.add_argument("--headless")
driver = webdriver.Chrome(desired_capabilities=caps,options=options)
driver.get('https://www.twitch.tv/auronplay/v/1202419629?sr=a&t=1s')

# driver.find_element_by_id("play-button").click()


def process_browser_log_entry(entry):
    response = json.loads(entry['message'])['message']
    return response

while True:
    browser_log = driver.get_log('performance') 
    events = [process_browser_log_entry(entry) for entry in browser_log]
    events = [event for event in events if 'Network.requestWillBeSentExtraInfo' in event['method']]

    # print(events)

    # val = json.dumps(events)
    # with open('txid.json','a') as f:
    #     f.write(val)

    # break

    for e in events:
        # print(e)
        try:
            protocol = 'http://'
            authority = e['params']['headers'][':authority']
            path = e['params']['headers'][':path']
            method = e['params']['headers'][':method']

            # if method == 'GET':

            # print(authority)
            if authority == 'd1m7jfoe9zdc1j.cloudfront.net':
                url = f"{protocol}{authority}{path}"
                print(url)
                break
            if '.m3u8' in path:
                print('M3U8 path', path)
            # url = f"{protocol}{authority}{path}"
            # print(url)
            # break
            
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