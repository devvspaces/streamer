import requests


base_url = 'http://d1m7jfoe9zdc1j.cloudfront.net/292814ab4c1804b18230_ninimusic1001_44392894813_1636644980/160p30/'

urls = []

with open('dvr.m3u8', 'r') as w:
    for i in w.readlines():
        i = i.strip('\n')
        if i.endswith('.ts'):
            urls.append(i)

print(urls)

for i in urls[:10]:
    r1 = requests.get(base_url+i, stream=True)
    if(r1.status_code == 200):
        with open('testvod.mpeg','ab') as f:
            for chunk in r1.iter_content(chunk_size=1024):
                f.write(chunk)
            print('Downloaded 10%')
    else:
        print("Received unexpected status code {}".format(r1.status_code))