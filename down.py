import requests

print("Recording video...")
response = requests.get("https://youtu.be/5qap5aO4i9A")
filename = time.strftime("%Y%m%d%H%M%S",time.localtime())+".avi"
f = open(filename, 'wb')

video_file_size_start = 0  
video_file_size_end = 1048576 * 7  # end in 7 mb 
block_size = 1024

while True:
   try:
      buffer = response.read(block_size)
      if not buffer:
         break
      video_file_size_start += len(buffer)
      if video_file_size_start > video_file_size_end:
         break
      f.write(buffer)

   except (Exception) as e:
      logger.exception(e)
f.close()