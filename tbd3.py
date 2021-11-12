import requests
data = {
    'api_token': 'ef79062c024af1b81ff8059bd198599e',
    'url': 'https://www.opdsupport.com/downloads/miscellaneous/sample-audio-files/52-welcome-wav/download',
    'return': 'apple_music,spotify',
}
result = requests.post('https://api.audd.io/', data=data)
print(result.text)