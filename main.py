import os
from dataclasses import dataclass
from pathlib import Path
import csv
from datetime import timedelta
import dotenv
from openai import OpenAI
from openai.types.audio.transcription_verbose import TranscriptionVerbose, TranscriptionSegment
from pydub import AudioSegment

SOURCE_DIR = "src"
PROCESSING_DIR = "pre"
OUTPUT_DIR = "out"

dotenv.load_dotenv()
api_key = os.environ.get("API_KEY")
if not api_key:
    raise SystemExit("API_KEY env var must be set")
client = OpenAI(api_key=api_key)


@dataclass
class AudioPart():
    filepath: str
    start: int
    end: int


def process_files(dirpath: str):
    files: list[str] = []
    for file in files:
        process_file(file)

# FILE -> PART -> SEGMENTS

def process_file(filepath: str):
    print(f"=== PROCESSING FILE: {filepath}")
    filename = os.path.basename(filepath)
    basename = os.path.splitext(filename)[0]
    extension = os.path.splitext(filename)[1]
    language = detect_language(basename)
    print(f"==> basename={basename}, extension={extension}, language={language}")
    
    # FILE into parts
    parts = split_file(filepath, filename, basename)

    # PARTS - text to speech
    segments: list[TranscriptionSegment] = []
    for i, part in enumerate(parts):
        print(f"\n===== {i+1:03d} PROCESSING PART: {part.filepath}")
        transcription = process_part(part, language)
        transcription.segments
        if transcription.segments is None:
            continue
        segments = segments + transcription.segments
        if i >= 2:
            break

    # OUT
    save_as_csv(segments, basename)


def detect_language(basename: str) -> str:
    splitted = basename.split("-")
    accepted_languages = ['en', 'cs', 'de']
    err_msg = f"Make sure input files have format '<something>-<language>.<extension>'. Where <language> is one of {accepted_languages}."
    if len(splitted) == 0:
        raise SystemExit(f"No '-' separator found in filename. {err_msg}")
    
    lang = splitted[-1]
    if lang not in accepted_languages:
        raise SystemExit(f"Detected language '{lang}' unsupported. {err_msg}")

    return lang


def save_as_csv(segments: list[TranscriptionSegment], basename: str):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    csv_path = os.path.join(OUTPUT_DIR, f"{basename}.csv")
    with open(csv_path, "w") as file:
        writer = csv.DictWriter(file, fieldnames=["segment number", "overlap", "start_secs", "end_secs", "start", "end", "text"])
        writer.writeheader()
        for i, segment in enumerate(segments):
            overlap = ""
            if segment.id == 0 and i != 0:
                overlap = "YES"
            start = round(segment.start, 0)
            end = round(segment.end, 0)
            row = {
                "segment number": i+1,
                "overlap": overlap,
                "start_secs": start,
                "end_secs": end,
                "start": str(timedelta(seconds=start)),
                "end": str(timedelta(seconds=end)),
                "text": segment.text.strip(),
                }
            writer.writerow(row)
    print(f"\n\n===== CSV exported: {csv_path}")


def process_part(part: AudioPart, language: str):
    transcription = speech_to_text(part.filepath, language)
    if transcription.segments is None:
        return transcription

    for segment in transcription.segments:
        segment.start = segment.start + part.start / 1000 # pydub stores time in ms, openai in seconds
        segment.end = segment.end + part.start / 1000 # so converting pydub to seconds
        print(f"{segment.start}->{segment.end}: {segment.text}")
        
    return transcription


def split_file(filepath: str, filename: str, basename: str):
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
        
        parts.append(AudioPart(part_path, start_time, end_time))
        start_time += part_duration - overlap_duration
        part_number += 1

    print("--> All parts ready!")
    return parts


def speech_to_text(filepath: str, language: str) -> TranscriptionVerbose:
    file = open( filepath, "rb")
    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        language=language,
        file=file,
        response_format="verbose_json",
        timestamp_granularities=["segment"],
    )
    return transcription


def save_transcription(text: str, out_path: str):
    with open(out_path, "w", encoding="utf-8") as output_file:
        output_file.write(text)
    print(f"Transcription saved to {out_path}")





if __name__ == "__main__":
    process_file("src/1-favu-cs.m4a")


