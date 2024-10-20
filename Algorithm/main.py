import time
import sys
#sys.path.insert(1,"c:/users/keith/appdata/local/programs/python/python39/lib/site-packages")
from flask import Flask, request, jsonify
from flask_cors import CORS
from ultralytics import YOLO
import cv2
import os
import numpy as np
import logging
import Algo
import glob
import pickle
from Algo import *

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app)
#model = load_model()
#model = YOLO('best_supernew.pt')
model = YOLO('best_plsplspls.pt')
modelt2 = YOLO('best_plsplspls.pt')
FOCUS_LEN = 3.04
CARD_LEN = 46
BULLEYE_LEN = 42
SENSOR_WIDTH = 3.68
SENSOR_HEIGHT = 2.76
PIXEL_WIDTH = 1024
PIXEL_HEIGHT = 768
OFFSET = 2.5 # in units / dm
CAR_START = (0.5, 0, np.pi/2)
CAR_END = (2.5, 0, -np.pi/2)
DISTANCE1 = 10
DIR1 = "L"

@app.route('/status', methods=['GET'])
def status():
    """
    This is a health check endpoint to check if the server is running
    :return: a json object with a key "result" and value "ok"
    """
    return jsonify({"result": "ok"})

# @app.route('/path', methods=['GET'])
# def path():
#     """
#     This is a health check endpoint to check if the server is running
#     :return: a json object with a key "result" and value "ok"
#     """
#     print(request.get_json())
#     targets = request.get_json()['targets']
#     targetls = [Algo.Target(y, x, rad) for y, x, rad in targets]
#     env = Grid(targetls.copy())
#     order, path = [], []
#     dp(targetls, env=env, order=order, path=path, algo_car=Algo.ReedsShepp, algo_search=rrt)

    
#     return jsonify({"stm": write_stm(path),
#                     "android": write_path(path)})
@app.route('/path', methods=['GET'])
def path():
    """
    This is a health check endpoint to check if the server is running
    :return: a json object with a key "result" and value "ok"
    """
    request_data = request.get_json()
    targets = request_data['targets']
    radius = request_data.get('radius', 2)
    algo_search = request_data.get('algo_search', 'hstar')
    # testing hstar
    # algo_search = request_data.get('algo_search', 'hstar')
    algo_car = request_data.get('algo_car', 'ReedsShepp')
    targetls = [Algo.Target(y, x, rad, id) for y, x, rad, id in targets]
    env = Grid(targetls.copy(), turning=request_data.get('turning', 1.2), straight=request_data.get('straight', 0.8))

    '''if algo_search == 'hstar':
        algo_search = hstar
    elif algo_search == 'astar':
        algo_search = astar #bad
    else:
        algo_search = rrt '''
    
    # testing hstar
    if algo_search == 'hstar':
        algo_search = hstar
    elif algo_search == 'astar':
        algo_search = astar #bad
    elif algo_search == 'rrt':
        algo_search = rrt
    else:
        algo_search = rrt

    if algo_car == 'Dubins':
        algo_car = Dubins
    else:
        algo_car = ReedsShepp

    order, path = [], []
    dp(targetls, env=env, order=order, path=path, algo_car=algo_car, algo_search=astar, radius=2.4)
    
    paths = {"paths": []}
    for p, target in zip(path, order):
        paths["paths"].append({"target": target.id, "stm": write_stm(p), "android": write_path(p), "finished": False})
    
    paths["paths"][-1]["finished"] = True

    return jsonify(paths)



@app.route('/image', methods=['POST'])
def image_predict():
    logging.debug("Received image prediction request")
    if 'file' not in request.files:
        logging.error("No file part in the request")
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        logging.error("No file selected")
        return jsonify({"error": "No file selected"}), 400

    if file:
        filename = file.filename
        logging.debug(f"Received file: {filename}")
        
        upload_dir = os.path.join(os.path.dirname(__file__), 'uploads')
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        file_path = os.path.join(upload_dir, filename)
        
        try:
            file.save(file_path)
            logging.debug(f"File saved successfully: {file_path}")
        except Exception as e:
            logging.error(f"Failed to save file: {str(e)}")
            return jsonify({"error": f"Failed to save file: {str(e)}"}), 500

        obstacle_id = os.path.splitext(filename)[0]

        try:
            image_id, annotated_image = predict_image_week_9(filename, model)
            logging.debug(f"Prediction successful. Image ID: {image_id}")
            
            # Save the annotated image
            prediction_dir = os.path.join(os.path.dirname(__file__), 'predictions')
            if not os.path.exists(prediction_dir):
                os.makedirs(prediction_dir)
            annotated_file_path = os.path.join(prediction_dir, f"annotated_{filename}")
            cv2.imwrite(annotated_file_path, annotated_image)
            logging.debug(f"Annotated image saved: {annotated_file_path}")
        except Exception as e:
            logging.error(f"Error in predict_image_week_9: {str(e)}")
            return jsonify({"error": f"Prediction failed: {str(e)}"}), 500

        result = {
            "obstacle_id": obstacle_id,
            "image_id": image_id
        }
        #logging.debug(f"Returning result: {result}")
        return jsonify(result)

    logging.error("Unknown error occurred")
    return jsonify({"error": "Unknown error occurred"}), 500

@app.route('/distance_one', methods=['POST'])
def distance_single():# Read the image
    file = request.files['file']
    if file:
        filename = file.filename
        logging.debug(f"Received file: {filename}")
        
        upload_dir = os.path.join(os.path.dirname(__file__), 'uploads')
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        file_path = os.path.join(upload_dir, filename)
        
        try:
            file.save(file_path)
            logging.debug(f"File saved successfully: {file_path}")
        except Exception as e:
            logging.error(f"Failed to save file: {str(e)}")
            return jsonify({"error": f"Failed to save file: {str(e)}"}), 500
    img = cv2.imread(os.path.join('uploads', filename))

    # Get the optimal camera matrix for better undistortion
    # dist_pickle = pickle.load(open('dist_pickle.p', 'rb'))
    # camera_matrix = dist_pickle['mtx']
    # dist_coeffs = dist_pickle['dist']
    
    # h, w = img.shape[:2]
    # new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, dist_coeffs, (w, h), 1, (w, h))

    # Undistort the image
    # undistorted_img = cv2.undistort(img, camera_matrix, dist_coeffs, None, new_camera_matrix)
    # x, y, w, h = roi
    # undistorted_img = undistorted_img[y:y+h, x:x+w]

    # img = cv2.resize(undistorted_img, (1024, 720))
    
    # Perform inference
    results = modelt2(img)
    
    # Process results
    detections = results[0].boxes.data  # Get detection data
    
    # Extract class IDs of detected objects
    class_ids = detections[:, 5].cpu().numpy().astype(int)

    # Define the name_to_id dictionary
    name_to_id = {
        "NA": 'NA',
        "20:A": 0,
        "21:B": 1,
        "0:Bullseye": 2,
        "22:C": 3,
        "23:D": 4,
        "24:E": 5,
        "25:F": 6,
        "26:G": 7,
        "27:H": 8,
        "28:S": 9,
        "29:T": 10,
        "30:U": 11,
        "31:V": 12,
        "32:W": 13,
        "33:X": 14,
        "34:Y": 15,
        "35:Z": 16,
        "40:Circle": 17,
        "37:Down Arrow": 18,
        "18:Eight": 19,
        "15:Five": 20,
        "14:Four": 21,
        "39:Left Arrow": 22,
        "19:Nine": 23,
        "11:One": 24,
        "38:Right Arrow": 25,
        "17:Seven": 26,
        "16:Six": 27,
        "13:Three": 28,        
        "12:Two": 29,
        "36:Up Arrow": 30
    }

    # name_to_id = {
    #     "0:Bullseye": 0,
    #     "39:Left Arrow": 1,
    #     "38:Right Arrow": 2,
    # }
    
    # Create a reverse mapping
    id_to_name = {v: k for k, v in name_to_id.items() if v != 'NA'}
    
    # Get the most common class ID (excluding background class if applicable)
    if len(class_ids) > 0:
        most_common_id = np.bincount(class_ids).argmax()
        image_id = id_to_name.get(most_common_id, 'NA')
    else:
        image_id = 'NA'  # No detection
    

    output = {"path": [], "det": []}
    # # Annotate the image
    for det in detections:
        bbox = det[:4].cpu().numpy()
        print(bbox)
        height = abs(bbox[3] - bbox[1])
        width = abs(bbox[2] - bbox[0])
        conf = det[4].cpu().numpy()
        class_id = int(det[5].cpu().numpy())
        # if class_id == 0:
        #     continue
        # if class_id != 1 and class_id != 2:
        #     continue
        # Get the class name
        class_name = id_to_name.get(class_id, 'Unknown')
        
        # width, height = (height + width) /2, (height + width) /2

        # Draw bounding box
        if class_id == 2:
            print("bullseye")
        distance1 = (FOCUS_LEN * CARD_LEN * PIXEL_WIDTH) / (width * SENSOR_WIDTH)
        distance2 = (FOCUS_LEN * CARD_LEN * PIXEL_HEIGHT) / (height * SENSOR_HEIGHT)
        distance = max(distance1, distance2)
        avg_distance = distance / 100
        DISTANCE1 = avg_distance
        print(DISTANCE1)
        if class_id == 22: #Turn left
            dist, path = Dubins.lsr(CAR_START, (CAR_START[0]+(avg_distance), CAR_START[1]-OFFSET, CAR_START[2]), 2.4)
            DIR1 = "L"
            output["path"] = write_stm(path)
        elif class_id == 25: #Turn right
            dist, path = Dubins.rsl(CAR_START, (CAR_START[0]+(avg_distance), CAR_START[1]+OFFSET, CAR_START[2]), 2.4)
            DIR1 = "R"
            output["path"] = write_stm(path)
        else:
            continue
        print(DIR1)
        # Add label
        label = f"{class_name}: {conf:.2f}"
        bbox = bbox.astype(int)
        print(output["path"])
        cv2.rectangle(img, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)
        cv2.putText(img, label, (bbox[0], bbox[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        output["dist"] = float(DISTANCE1)
        output["dir1"] = DIR1
    # Save the annotated image
    annotated_image = img.copy()
    prediction_dir = os.path.join(os.path.dirname(__file__), 'predictions')
    if not os.path.exists(prediction_dir):
        os.makedirs(prediction_dir)
    annotated_file_path = os.path.join(prediction_dir, f"annotated_{filename}")
    cv2.imwrite(annotated_file_path, annotated_image)
    logging.debug(f"Annotated image saved: {annotated_file_path}")
    return jsonify(output)

@app.route('/distance_three', methods=['POST'])
def distance_triple():# Read the image
    file = request.files['file']
    distance = request.form.get("distance")
    dir1 = request.form.get("dir1")
    distance = float(distance)
    print(distance)
    print(dir1)
    if file:
        filename = file.filename
        logging.debug(f"Received file: {filename}")
        
        upload_dir = os.path.join(os.path.dirname(__file__), 'uploads')
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        file_path = os.path.join(upload_dir, filename)
        
        try:
            file.save(file_path)
            logging.debug(f"File saved successfully: {file_path}")
        except Exception as e:
            logging.error(f"Failed to save file: {str(e)}")
            return jsonify({"error": f"Failed to save file: {str(e)}"}), 500
    img = cv2.imread(os.path.join('uploads', filename))

    # Get the optimal camera matrix for better undistortion
    # dist_pickle = pickle.load(open('dist_pickle.p', 'rb'))
    # camera_matrix = dist_pickle['mtx']
    # dist_coeffs = dist_pic÷kle['dist']
    
    # h, w = img.shape[:2]
    # new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, dist_coeffs, (w, h), 1, (w, h))

    # Undistort the image
    # undistorted_img = cv2.undistort(img, camera_matrix, dist_coeffs, None, new_camera_matrix)
    # x, y, w, h = roi
    # undistorted_img = undistorted_img[y:y+h, x:x+w]

    # img = cv2.resize(undistorted_img, (1024, 720))
    
    # Perform inference
    results = modelt2(img)
    
    # Process results
    detections = results[0].boxes.data  # Get detection data
    
    # Extract class IDs of detected objects
    class_ids = detections[:, 5].cpu().numpy().astype(int)

    # Define the name_to_id dictionary
    name_to_id = {
        "NA": 'NA',
        "20:A": 0,
        "21:B": 1,
        "0:Bullseye": 2,
        "22:C": 3,
        "23:D": 4,
        "24:E": 5,
        "25:F": 6,
        "26:G": 7,
        "27:H": 8,
        "28:S": 9,
        "29:T": 10,
        "30:U": 11,
        "31:V": 12,
        "32:W": 13,
        "33:X": 14,
        "34:Y": 15,
        "35:Z": 16,
        "40:Circle": 17,
        "37:Down Arrow": 18,
        "18:Eight": 19,
        "15:Five": 20,
        "14:Four": 21,
        "39:Left Arrow": 22,
        "19:Nine": 23,
        "11:One": 24,
        "38:Right Arrow": 25,
        "17:Seven": 26,
        "16:Six": 27,
        "13:Three": 28,        
        "12:Two": 29,
        "36:Up Arrow": 30
    }

    # name_to_id = {
    #     "0:Bullseye": 0,
    #     "39:Left Arrow": 1,
    #     "38:Right Arrow": 2,
    # }
    
    # Create a reverse mapping
    id_to_name = {v: k for k, v in name_to_id.items() if v != 'NA'}
    
    # Get the most common class ID (excluding background class if applicable)
    if len(class_ids) > 0:
        most_common_id = np.bincount(class_ids).argmax()
        image_id = id_to_name.get(most_common_id, 'NA')
    else:
        image_id = 'NA'  # No detection
    
    if dir1 == "L":
        bullseye = (1000, None)
    else:
        bullseye = (-1, None)
    arrowls = []
    for det in detections:
        bbox = det[:4].cpu().numpy()
        conf = det[4].cpu().numpy()
        if conf < 0.3:
            continue
        center = (bbox[0] + bbox[2]) / 2
        class_id = int(det[5].cpu().numpy())
        if class_id == 2:
            if dir1 == "L":
                if center < bullseye[0]:
                    bullseye = (center, det)
            else:
                if center > bullseye[0]:
                    bullseye = (center, det)
        elif class_id == 22 or class_id == 25:
            arrowls.append(det)
        class_name = id_to_name.get(class_id, 'Unknown')
        label = f"{class_name}: {conf:.2f}"
        bbox = bbox.astype(int)
        cv2.rectangle(img, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)
        cv2.putText(img, label, (bbox[0], bbox[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    output = {"length/dist": [], "error": "NA", "path": []}

    # Save the annotated image
    annotated_image = img.copy()
    prediction_dir = os.path.join(os.path.dirname(__file__), 'predictions')
    if not os.path.exists(prediction_dir):
        os.makedirs(prediction_dir)
    annotated_file_path = os.path.join(prediction_dir, f"annotated_{filename}")
    cv2.imwrite(annotated_file_path, annotated_image)
    logging.debug(f"Annotated image saved: {annotated_file_path}")

    # Assume exactly 2 bullseyes and 1 arrow
    if len(arrowls) != 1:
        output["error"] = "Invalid number of bullseyes or arrows detected"
        return jsonify(output)
    
    arrow_bbox = arrowls[0][:4].cpu().numpy()
    class_id = int(arrowls[0][5].cpu().numpy())
    bullseye_bbox = bullseye[1][:4].cpu().numpy()
    ref_pt = (arrow_bbox[0] + arrow_bbox[2]) / 2
    bulleye_c1 = (bullseye_bbox[0] + bullseye_bbox[2]) / 2 # x
    if (class_id==22):
        output["dir2"]="L"
    else:
        output["dir2"]="R"
    

    width = abs(bullseye_bbox[2] - bullseye_bbox[0]).astype(float)
    height = abs(bullseye_bbox[3] - bullseye_bbox[1]).astype(float)
    b = estimate_distance(width, height, True)
    width = abs(arrow_bbox[2] - arrow_bbox[0]).astype(float)
    height = abs(arrow_bbox[3] - arrow_bbox[1]).astype(float)
    a = estimate_distance(width, height, False)

    print(a, b)
    m = np.sqrt(max(a**2 - (OFFSET*100)**2, 0))
    box_len = np.sqrt(max(b**2 - m**2, 0)) + OFFSET*100
    output["length/dist"].append((float(box_len), float(m)))
    print(box_len, m)
    box_len = box_len / 100
    m = m / 100
    print(box_len, m)
    path = []
    # box_len *= 2/3
    box_len = 6
    print(DIR1)
    if dir1 == "L":
        if class_id == 22: #left
            path += [Path(start=(CAR_START[0]+distance, CAR_START[1]-OFFSET, np.pi/2), len=1.5, forward=True)]
            dist, patht = Dubins.lsr((CAR_START[0]+distance+1.5, CAR_START[1]-OFFSET, np.pi/2), (CAR_START[0]+distance+m, CAR_START[1]-box_len-OFFSET, np.pi/2), 2.4)
            path += patht
            path += [Path(start=(CAR_START[0]+distance+m, CAR_START[1]-box_len-OFFSET, np.pi/2), len=2, forward=True)]
            dist, patht = Dubins.rsr((CAR_START[0]+distance+m+2, CAR_START[1]-box_len-OFFSET, np.pi/2), (CAR_START[0]+distance+m+2, CAR_START[1]+box_len+OFFSET, -np.pi/2), 2.4)
            path += patht
            path += [Path(start=(CAR_START[0]+distance+m+2, CAR_START[1]+box_len+OFFSET, -np.pi/2), len=2, forward=True)]
            dist, patht = Dubins.rsl((CAR_START[0]+distance+m, CAR_START[1]+box_len+OFFSET, -np.pi/2), CAR_END, 2.4)
            path += patht
        else:
            path += [Path(start=(CAR_START[0]+distance, CAR_START[1]-OFFSET, np.pi/2), len=1.5, forward=True)]
            dist, patht = Dubins.rsl((CAR_START[0]+distance+1.5, CAR_START[1]-OFFSET, np.pi/2), (CAR_START[0]+distance+m, CAR_START[1]+box_len+OFFSET, np.pi/2), 2.4)
            path += patht
            path += [Path(start=(CAR_START[0]+distance+m, CAR_START[1]+box_len+OFFSET, np.pi/2), len=2, forward=True)]
            dist, patht = Dubins.lsl((CAR_START[0]+distance+m+2, CAR_START[1]+box_len+OFFSET, np.pi/2), (CAR_START[0]+distance+m+2, CAR_START[1]-box_len-OFFSET, -np.pi/2), 2.4)
            path += patht
            path += [Path(start=(CAR_START[0]+distance+m+2, CAR_START[1]-box_len-OFFSET, -np.pi/2), len=2, forward=True)]
            dist, patht = Dubins.lsr((CAR_START[0]+distance+m, CAR_START[1]-box_len-OFFSET, -np.pi/2), CAR_END, 2.4)
            path += patht
    else:
        if class_id == 22: #left
            path += [Path(start=(CAR_START[0]+distance, CAR_START[1]+OFFSET, np.pi/2), len=1.5, forward=True)]
            dist, patht = Dubins.lsr((CAR_START[0]+distance+1.5, CAR_START[1]+OFFSET, np.pi/2), (CAR_START[0]+distance+m, CAR_START[1]-box_len-OFFSET, np.pi/2), 2.4)
            path += patht
            path += [Path(start=(CAR_START[0]+distance+m, CAR_START[1]-box_len-OFFSET, np.pi/2), len=3, forward=True)]
            dist, patht = Dubins.rsr((CAR_START[0]+distance+m+3, CAR_START[1]-box_len-OFFSET, np.pi/2), (CAR_START[0]+distance+m+3, CAR_START[1]+box_len+OFFSET, -np.pi/2), 2.4)
            path += patht
            path += [Path(start=(CAR_START[0]+distance+m+3, CAR_START[1]+box_len+OFFSET, -np.pi/2), len=3, forward=True)]
            dist, patht = Dubins.rsl((CAR_START[0]+distance+m, CAR_START[1]+box_len+OFFSET, -np.pi/2), CAR_END, 2.4)
            path += patht
        else:
            path += [Path(start=(CAR_START[0]+distance, CAR_START[1]+OFFSET, np.pi/2), len=1.5, forward=True)]
            dist, patht = Dubins.rsl((CAR_START[0]+distance+1.5, CAR_START[1]+OFFSET, np.pi/2), (CAR_START[0]+distance+m, CAR_START[1]+box_len+OFFSET, np.pi/2), 2.4)
            path += patht
            path += [Path(start=(CAR_START[0]+distance+m, CAR_START[1]+box_len+OFFSET, np.pi/2), len=2, forward=True)]
            dist, patht = Dubins.lsl((CAR_START[0]+distance+m+2, CAR_START[1]+box_len+OFFSET, np.pi/2), (CAR_START[0]+distance+m+2, CAR_START[1]-box_len-OFFSET, -np.pi/2), 2.4)
            path += patht
            path += [Path(start=(CAR_START[0]+distance+m+2, CAR_START[1]-box_len-OFFSET, -np.pi/2), len=2, forward=True)]
            dist, patht = Dubins.lsr((CAR_START[0]+distance+m, CAR_START[1]-box_len-OFFSET, -np.pi/2), CAR_END, 2.4)
            path += patht

    output["path"] = [write_stm(path)]
    
    return jsonify(output)


# @app.route('/stitch', methods=['GET'])
# def stitch():
#     """
#     This is the main endpoint for the stitching command. Stitches the images using two different functions, in effect creating two stitches, just for redundancy purposes
#     """
#     img = stitch_image()
#     img.show()
#     img2 = stitch_image_own()
#     img2.show()
#     return jsonify({"result": "ok"})
@app.route('/stitch', methods=['GET'])
def stitch():
    try:
        upload_dir = r'/Users/yanchi/Downloads/MDP_Algo 3/predictions'
        
        image_paths = glob.glob(os.path.join(upload_dir,'*.jpg'))
        if len(image_paths) == 0:
            return jsonify({"error": "No images found in the folder to stitch."}), 400
        images = [cv2.imread(image_path) for image_path in image_paths]
        stitched_image = stitch_images(images, mode='vertical')

        stitched_image_path = os.path.join(upload_dir, 'stitched_image.jpg')
        cv2.imwrite(stitched_image_path, stitched_image)

        logging.debug(f"Stitched image saved: {stitched_image_path}")

        return jsonify({"result": "ok", "stitched_image_path": stitched_image_path})
    except Exception as e:
        logging.error(f"Error in stitching images: {str(e)}")
        return jsonify({"error": f"Stitching failed: {str(e)}"}),500
    
def stitch_images(images, mode='vertical'):
    if mode == 'vertical':
        stitched_image = np.vstack(images)
    elif mode == 'horizontal':
        stitched_image = np.hstack(images)
    elif mode == 'grid':
        rows = []
        row_images = [np.hstack(images[i:i+2]) for i in range(0, len(images), 2)]
        stitched_image = np.vstack(row_images)
    else:
        raise ValueError("Mode must be 'horizontal', 'vertical', or 'grid'")
    
    return stitched_image

def predict_image_week_9(filename, model):
    # Read the image
    img = cv2.imread(os.path.join('uploads', filename))
    
    # Perform inference
    results = model(img)

    #print(results2[0].boxes)
    
    # Process results
    detections = results[0].boxes.data  # Get detection data
    
    # Extract class IDs of detected objects
    class_ids = detections[:, 5].cpu().numpy().astype(int)

    if len(detections) == 0:
        return 'NA', img
    bounding_boxes = detections[:,:4].cpu().numpy().astype(int)
    areas = (bounding_boxes[:,2] - bounding_boxes[:,0]) * (bounding_boxes[:,3] - bounding_boxes[:,1])
    closest_idx = np.argmax(areas)

    # Define the name_to_id dictionary
    #"0:Bullseye": 2,
    name_to_id = {
        "NA": 'NA',
        "20:A": 0,
        "21:B": 1,
        "0:Bullseye": 2,
        "22:C": 3,
        "23:D": 4,
        "24:E": 5,
        "25:F": 6,
        "26:G": 7,
        "27:H": 8,
        "28:S": 9,
        "29:T": 10,
        "30:U": 11,
        "31:V": 12,
        "32:W": 13,
        "33:X": 14,
        "34:Y": 15,
        "35:Z": 16,
        "40:Circle": 17,
        "37:Down Arrow": 18,
        "18:Eight": 19,
        "15:Five": 20,
        "14:Four": 21,
        "39:Left Arrow": 22,
        "19:Nine": 23,
        "11:One": 24,
        "38:Right Arrow": 25,
        "17:Seven": 26,
        "16:Six": 27,
        "13:Three": 28,        
        "12:Two": 29,
        "36:Up Arrow": 30
    }
    
    # Create a reverse mapping
    id_to_name = {v: k for k, v in name_to_id.items() if v != 'NA'}
    
    closest_class_id = class_ids[closest_idx]
    closest_bbox = bounding_boxes[closest_idx]
    image_id = id_to_name.get(closest_class_id,'NA')
    bbox = closest_bbox
    conf = detections[closest_idx,4].cpu().numpy()
    cv2.rectangle(img, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0,255,0), 2)
    label = f"{image_id}:{conf:.2f}"
    cv2.putText(img,label,(bbox[0], bbox[1] - 10), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 0.5, (0,255,0), 2)


    # Get the most common class ID (excluding background class if applicable)
    # if len(class_ids) > 0:
    #     most_common_id = np.bincount(class_ids).argmax()
    #     image_id = id_to_name.get(most_common_id, 'NA')
    # else:
    #     image_id = 'NA'  # No detection
    
    # # Annotate the image
    # for det in detections:
    #     bbox = det[:4].cpu().numpy().astype(int)
    #     conf = det[4].cpu().numpy()
    #     class_id = int(det[5].cpu().numpy())
        
    #     # Get the class name
    #     class_name = id_to_name.get(class_id, 'Unknown')
        
    #     # Draw bounding box
    #     cv2.rectangle(img, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)
        
    #     # Add label
    #     label = f"{class_name}: {conf:.2f}"
    #     cv2.putText(img, label, (bbox[0], bbox[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    #Return the image id and annotated image
    return image_id, img.copy()

def write_path(path):
    ss = ""
    for p in path:
        for coords in p.path_coords:
            ss += f"{coords[0]:.2f} {coords[1]:.2f} {coords[2]:.2f}\n"


    return ss

def write_stm(path):
    ss = ""
    for p in path:
        if p.forward and p.straight:
            curlen = p.len
            while curlen > 9:
                ss += f"FW{round(9*10):0>2}\n"
                curlen -= 9
            ss += f'FW{round(curlen*10):0>2}\n'
        elif p.forward and not p.straight and p.steering=="R":
            curangle = p.angle
            while curangle > np.pi/2:
                ss += f"FR{round(90):0>2}\n"
                curangle -= np.pi/2
            if round(curangle/np.pi * 180) > 0:
                ss += f"FR{round(curangle/np.pi * 180):0>2}\n"
        elif p.forward and not p.straight and p.steering=="L":
            curangle = p.angle
            while curangle > np.pi/2:
                ss += f"FL{round(90):0>2}\n"
                curangle -= np.pi/2
            if round(curangle/np.pi * 180) > 0:
                ss += f"FL{round(curangle/np.pi * 180):0>2}\n"
        elif not p.forward and p.straight:
            curlen = p.len
            while curlen > 9:
                ss += f"BW{round(9*10):0>2}\n"
                curlen -= 9
            ss += f'BW{round(curlen*10):0>2}\n'
        elif not p.forward and not p.straight and p.steering=="R":
            curangle = p.angle
            while curangle > np.pi/2:
                ss += f"BR{round(90):0>2}\n"
                curangle -= np.pi/2
            if round(curangle/np.pi * 180) > 0:
                ss += f"BR{round(curangle/np.pi * 180):0>2}\n"
        elif not p.forward and not p.straight and p.steering=="L":
            curangle = p.angle
            while curangle > np.pi/2:
                ss += f"BL{round(90):0>2}\n"
                curangle -= np.pi/2
            if round(curangle/np.pi * 180) > 0:
                ss += f"BL{round(curangle/np.pi * 180):0>2}\n"
    return ss

def estimate_distance(width, height, bulleye):
    v = (height + width) / 2
    if bulleye:
        distance1 = (FOCUS_LEN * BULLEYE_LEN * PIXEL_WIDTH) / (v * SENSOR_WIDTH)
        distance2 = (FOCUS_LEN * BULLEYE_LEN * PIXEL_HEIGHT) / (v * SENSOR_HEIGHT)
    else:
        distance1 = (FOCUS_LEN * CARD_LEN * PIXEL_WIDTH) / (v * SENSOR_WIDTH)
        distance2 = (FOCUS_LEN * CARD_LEN * PIXEL_HEIGHT) / (v * SENSOR_HEIGHT)
    avg_distance = (distance1 + distance2) / 2
    return avg_distance

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)

