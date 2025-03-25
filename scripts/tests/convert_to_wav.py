import os
from pydub import AudioSegment
# To run convert_to_wav script, you must install ffmpeg (if you have chocolatey, you can use that)
# Define the directory containing the mp4 files
# directory = r"path/to/tests"

directory = r"scripts/tests"

# Loop through all files in the directory
for filename in os.listdir(directory):
    if filename.endswith(".mp4"):
        # Construct the full file path
        input_file = os.path.join(directory, filename)
        # Construct the output file path
        output_file = os.path.splitext(input_file)[0] + ".wav"
        # Load the mp4 file
        audio = AudioSegment.from_file(input_file, format="mp4")
        # Export as wav
        audio.export(output_file, format="wav")