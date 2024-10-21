import time
from picamera import PiCamera
import io
import requests


# Global counter for image naming
image_counter = 0

def capture_image(picam2, inference_server, data=None):
    global image_counter
    stream = io.BytesIO()
    picam2.capture(stream, format='jpeg')
    stream.seek(0)

    # Increment the counter and create a unique filename
    image_counter += 1
    filename = f"image_{image_counter}.jpg"
    
    # Send the image to the server
    print ('sending to server')
    result = send_image_to_server(stream, filename, inference_server, data)
    print ('received from server')
    if result:
        print("Server Response:")
        print(f"Obstacle ID: {result.get('obstacle_id', 'N/A')}")
        print(f"Image ID: {result.get('image_id', 'N/A')}")
    else:
        print("Failed to get a valid response from the server.")
    
    stream.truncate(0)
    return result
    

def send_image_to_server(image_stream, filename, inference_server, data=None):
    files = {'file': (filename, image_stream, 'image/jpeg')}
    try:
        response = requests.post(inference_server, files=files, data=data)
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