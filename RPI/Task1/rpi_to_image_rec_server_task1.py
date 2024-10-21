import time
from picamera import PiCamera
import io
import requests


# Inference server URL
INFERENCE_SERVER_URL = "http://192.168.29.15:5002/image"
print ('Server Connected')
# Global counter for image naming
image_counter = 0

def capture_image(picam2):
    global image_counter
    stream = io.BytesIO()
    picam2.capture(stream, format='jpeg')
    stream.seek(0)

    # Increment the counter and create a unique filename
    image_counter += 1
    filename = f"image_{image_counter}.jpg"
    
    # Send the image to the server
    print ('sending to server')
    result = send_image_to_server(stream, filename)
    print ('received from server')
    if result:
        print("Server Response:")
        print(f"Obstacle ID: {result.get('obstacle_id', 'N/A')}")
        print(f"Image ID: {result.get('image_id', 'N/A')}")
    else:
        print("Failed to get a valid response from the server.")
    
    stream.truncate(0)
    return result.get('image_id', 'N/A')
    

def send_image_to_server(image_stream, filename):
    files = {'file': (filename, image_stream, 'image/jpeg')}
    try:
        response = requests.post(INFERENCE_SERVER_URL, files=files)
        print(f"Server response status code: {response.status_code}")
        print(f"Server response content: {response.text}")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: Server responded with status code {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error sending request to server: {e}")
        return None

if __name__ == "__main__":
    capture_image()