import subprocess
import whisper
import json
from pathlib import Path
import os
from dotenv import load_dotenv
from groq import Groq


num_clips = input("Number of Clips: ")
while not num_clips.isdigit() or int(num_clips) <= 0:
    print("Number of Clips must be a whole number above 0")
    num_clips = input("Number of Clips: ")

model_size = input("Model Size (tiny, base, small, medium, large): ").lower()
sizes = ["tiny", "base", "small", "medium", "large"]
while model_size not in sizes:
    print("Model Size must strictly be tiny, base, small, medium, large")
    model_size = input("Model Size: ").lower()

NUMBER_OF_CLIPS = int(num_clips)
MODEL_SIZE = model_size
PADDING = 10

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

'''
Create or load transcript.json
'''

TRANSCRIPT_FILE = f"transcript_{MODEL_SIZE}.json"

if Path(TRANSCRIPT_FILE).exists():
    print(f"{TRANSCRIPT_FILE} already exists — Loading...")
    with open(TRANSCRIPT_FILE) as f:
        segments = json.load(f)

else:
    model = whisper.load_model(MODEL_SIZE)
    result = model.transcribe("audio.wav")

    segments = []
    for seg in result["segments"]:
        segments.append({
            "start": round(seg["start"], 2),
            "end": round(seg["end"], 2),
            "text": seg["text"].strip()
        })

    with open(TRANSCRIPT_FILE, "w") as f:
        json.dump(segments, f, indent=2)
    print(f"Saved new {TRANSCRIPT_FILE}")

'''
Select and save the best clips using groq
'''

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Turn the segment lists into txt
transcript_text = "\n".join(
    f"[{seg['start']}s - {seg['end']}s] {seg['text']}"
    for seg in segments
)

prompt = f"""Here is a timestamped transcript from a video:

{transcript_text}

Pick the {NUMBER_OF_CLIPS} best moments from this transcript for short-form
video clips (like YouTube Shorts or TikTok). Choose moments that are
engaging, funny, surprising, or emotionally strong -- not just long ones.

Respond with ONLY a JSON array, no other text, in this exact format:
[
  {{"start": 139.0, "end": 143.0, "text": "the spoken text", "reason": "why this is a good clip"}}
]
"""

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": prompt}]
)

raw_reply = response.choices[0].message.content
best_moments = json.loads(raw_reply)

print(f"Picked {len(best_moments)} moments:\n")
for m in best_moments:
    print(f"{m['start']}s - {m['end']}s: {m['text']}")
    print(f"  Reason: {m['reason']}\n")

with open("best_moments.json", "w") as f:
    json.dump(best_moments, f, indent=2)

print("Successfully saved moments to best_moments.json")


'''
Cut each picked moment out of video.mp4 into its own clip file
'''

clip_number = 1

for moment in best_moments:
    start = max(0, moment["start"] - PADDING)
    end = moment["end"] + PADDING
    duration = end - start
    output_name = f"{MODEL_SIZE}_clip_{clip_number}.mp4"

    subprocess.run([
        "ffmpeg",
        "-y",
        "-i", "video.mp4",
        "-ss", str(start),   
        "-t", str(duration),
        output_name
    ])

    clip_number += 1

print("\nDone. Check this folder for your clips.")