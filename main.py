import os
from dataclasses import dataclass
from pathlib import Path
import dotenv
from openai import OpenAI
from openai.types.audio.transcription_verbose import TranscriptionVerbose
from pydub import AudioSegment

SOURCE_DIR = "src"
PROCESSING_DIR = "pre"
OUTPUT_DIR = "out"

dotenv.load_dotenv()
api_key = os.environ.get("API_KEY")
if not api_key:
    raise SystemExit("API_KEY env var must be set")
client = OpenAI(api_key=api_key)


def process_files(dirpath: str):
    files: list[str] = []
    for file in files:
        process_file(file)

# FILE -> PART -> SEGMENTS

def process_file(filepath: str):
    # FILE into parts
    parts = split_file(filepath)

    return
    # PARTS - text to speech

    for part in parts:
        transcription = speech_to_text(part)


    # Speech-to-text
    json = speech_to_text(filepath)



    # OUT
    base_filename = os.path.basename(filepath)
    base_name_without_ext = os.path.splitext(base_filename)[0]
    output_file_path = os.path.join("out", f"{base_name_without_ext}.srt")
    

def process_part(part_path: str, start: float):
    part_path = "pre/segment_001.m4a"
    transcription = speech_to_text(part_path)
    if transcription.segments is None:
        return

    for segment in transcription.segments:
        print(f"{segment.start}->{segment.end}\n{segment.text}")


@dataclass
class AudioPart():
    filepath: str
    start: int
    end: int

def split_file(filepath: str):
    filename = os.path.basename(filepath)
    basename = os.path.splitext(filename)[0]
    output_dir = os.path.join(PROCESSING_DIR, basename)
    os.makedirs(output_dir, exist_ok=True)
    audio = AudioSegment.from_file(filepath)

    # Parameters for trimming
    part_duration = 5 * 60 * 1000  # 5 minutes in milliseconds
    overlap_duration = 10 * 1000  # 10 seconds in milliseconds

    parts: list[AudioPart] = []
    start_time = 0
    part_number = 1
    while start_time < len(audio):
        end_time = start_time + part_duration
        if end_time > len(audio):
            end_time = len(audio)

        part_filename = f"part{part_number:03d}_{start_time}.m4a"
        part_path = os.path.join(output_dir, part_filename)

        if Path(part_path).is_file():
            print(f"{part_number:03d} skipped: file already exists {part_path}")
        else:
            part = audio[start_time:end_time]        
            part.export(part_path, format="ipod")
            print(f"{part_number:03d} exported: {part_path} (start={start_time})")
        
        parts.append(AudioPart(part_filename, start_time, end_time))
        start_time += part_duration - overlap_duration
        part_number += 1

    print("All parts ready.")
    return parts


def speech_to_text(filepath: str) -> TranscriptionVerbose:
    file = open( filepath, "rb")
    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        language="cs",
        file=file,
        response_format="verbose_json",
        timestamp_granularities=["segment"],
        temperature=0.1,
    )
    return transcription


def save_transcription(text: str, out_path: str):
    with open(out_path, "w", encoding="utf-8") as output_file:
        output_file.write(text)
    print(f"Transcription saved to {out_path}")





if __name__ == "__main__":
    process_file("src/1-favu-cs.m4a")


