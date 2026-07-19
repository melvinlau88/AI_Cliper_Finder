import subprocess

'''
Extracts the audio track from video.mp4 and saves it as audio.wav,
converted to the format (16kHz, mono)
'''
subprocess.run([
    "ffmpeg",
    "-y",
    "-i", "video.mp4",     
    "-vn",                 
    "-ar", "16000",
    "-ac", "1",         
    "audio.wav"             
])

