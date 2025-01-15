import os
from openai import OpenAI
from openai.types.audio.transcription_verbose import TranscriptionVerbose
import dotenv

dotenv.load_dotenv()
api_key = os.environ.get("API_KEY")
if not api_key:
    raise SystemExit("API_KEY env var must be set")
client = OpenAI(api_key=api_key)


def process_files(dirpath: str):
    files: list[str] = []
    for file in files:
        process_file(file)


def process_file(filepath: str):
    # Prepare
    splitted = split_file(filepath)


    # Speech-to-text
    json = speech_to_text(filepath)


    # OUT
    base_filename = os.path.basename(filepath)
    base_name_without_ext = os.path.splitext(base_filename)[0]
    output_file_path = os.path.join("out", f"{base_name_without_ext}.srt")
    


def split_file(filepath: str):
    pass
    return #parts


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





file = "pre/segment_001.m4a"
transcription = speech_to_text(file)

for segment in transcription.segments:
    print(f"{segment.start}->{segment.end}\n{segment.text}")




