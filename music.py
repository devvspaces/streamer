import moviepy.editor as mp

my_clip = mp.VideoFileClip(r"testvod.mpeg")

my_clip.audio.write_audiofile(r"my_result.mp3")