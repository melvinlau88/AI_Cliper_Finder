import subprocess
import whisper
import json
from pathlib import Path

NUMBER_OF_CLIPS = 3

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

if Path("transcript.json").exists():
    print("transcript.json already exists — Loading...")
    with open("transcript.json") as f:
        segments = json.load(f)

else:
    # Load model and transcribe audio to text
    model = whisper.load_model("base")
    result = model.transcribe("audio.wav")

    # List of dictionaries for each chunk 
    segments = []
    for seg in result["segments"]:
        segments.append({
            "start": round(seg["start"], 2),
            "end": round(seg["end"], 2),
            "text": seg["text"].strip()
        })

    with open("transcript.json", "w") as f:
        json.dump(segments, f, indent=2)
    print("Saved new transcript.json")

'''
Select and save the best clips
'''

# Sort by video length
segments_by_length = sorted(
    segments,
    key=lambda seg: seg["end"] - seg["start"],
    reverse=True
)

# Take the top 'N' longest segments
best_moments = segments_by_length[0:NUMBER_OF_CLIPS]

# Put them back in chronological order
best_moments = sorted(best_moments, key=lambda seg: seg["start"])

# Print moments for sanity check
print(f"Picked {len(best_moments)} moments:\n")
for m in best_moments:
    print(f"{m['start']}s - {m['end']}s: {m['text']}")

# Save the best moments
with open("best_moments.json", "w") as f:
    json.dump(best_moments, f, indent=2)

print("\nSuccussfully saved moments to best_moments.json")


'''
Cut each picked moment out of video.mp4 into its own clip file
'''

clip_number = 1

for moment in best_moments:
    start = moment["start"]
    duration = moment["end"] - start
    output_name = f"clip_{clip_number}.mp4"

    subprocess.run([
        "ffmpeg",
        "-y",
        "-i", "video.mp4",
        "-ss", str(start),   
        "-t", str(duration),
        "final_clips"
    ])

    print(f"Saved {output_name} ({start}s - {moment['end']}s)")
    clip_number += 1

