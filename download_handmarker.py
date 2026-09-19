import urllib.request

url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
output_filename = "hand_landmarker.task"

print("Downloading hand tracking model file... please wait...")
urllib.request.urlretrieve(url, output_filename)
print(f"Download complete! File saved as '{output_filename}'.")