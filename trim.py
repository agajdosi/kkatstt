from pydub import AudioSegment
import os

# Specify the input audio file
input_file_path = "src/1-favu-cs.m4a"
output_directory = "pre"
os.makedirs(output_directory, exist_ok=True)

# Load the audio file
audio = AudioSegment.from_file(input_file_path)

# Parameters for trimming
segment_duration = 5 * 60 * 1000  # 5 minutes in milliseconds
overlap_duration = 10 * 1000  # 10 seconds in milliseconds

# Initialize variables
start_time = 0
segment_number = 1

# Trim audio into segments
while start_time < len(audio):
    end_time = start_time + segment_duration
    if end_time > len(audio):
        end_time = len(audio)

    # Extract segment
    segment = audio[start_time:end_time]

    # Export the segment to a file
    segment_filename = f"segment_{segment_number:03d}.m4a"
    segment_path = os.path.join(output_directory, segment_filename)
    #segment.export(segment_path, format="m4a")
    segment.export(segment_path, format="ipod")

    print(f"Exported: {segment_path}")

    # Update start_time with overlap
    start_time += segment_duration - overlap_duration
    segment_number += 1

print("All segments exported.")
