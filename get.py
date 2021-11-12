import requests
data = {
    'url': 'https://files.fm/down.php?cf&i=rhhjks84b&n=Ed_Sheeran_-_Thinking_Out_Loud-AFROBEAT.co.za.mp3',
    'return': 'apple_music,spotify',
    'api_token': 'ef79062c024af1b81ff8059bd198599e'
}
result = requests.post('https://api.audd.io/', data=data)
print(result.text)