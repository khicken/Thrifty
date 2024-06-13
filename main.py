from pricing import price
from ultralytics import YOLO
import cv2, math

vid = cv2.VideoCapture(0)

# For YOLO model (https://dipankarmedh1.medium.com/real-time-object-detection-with-yolo-and-webcam-enhancing-your-computer-vision-skills-861b97c78993)
model = YOLO("yolo-Weights/yolov8n.pt")
classNames = ["shirt", "pants", "shoes", "backpack", "umbrella", "handbag", "tie", # Clothing
              "glove", "gloves", "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", # Garments
              "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite", "baseball bat", # Sports Equipment
              "cup", "fork", "knife", "spoon", "bowl", "chair", "sofa", "pottedplant", "bed", # Cutlery
              "laptop", "mouse", "remote", "keyboard", "cell phone", "microwave", "oven", # Electronics, will be a hassle
              "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors", # Tools
              "teddy bear", "hair drier", "toothbrush", # Miscellaneous
              "person" # For...fun
              ]

while True:
    ret, img = vid.read() # Read video
    
    if not ret: # Camera not found error
        raise SystemError('Uh oh! Stinky!\nYour camera doesn\'t work.')
        break

    # Draw bounding boxes with labels
    results = model(img, stream=True)
    for r in results:
        boxes = r.boxes

        for box in boxes:
            # Bounding box
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2) # convert to int values

            # Place box in frame
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 3)

            # Metrics
            cls = int(box.cls[0]) # Class name (object type)
            confidence = math.ceil((box.conf[0]*100))/100 # Confidence

            # object details
            txt = f'{classNames[cls]} | Confidence: {confidence}'
            org = [x1, y1]
            font = cv2.FONT_HERSHEY_SIMPLEX
            fontScale = 1
            color = (255, 0, 0)
            thickness = 2
            cv2.putText(img, txt, org, font, fontScale, color, thickness)

    # Other window handling
    cv2.imshow('Object Detection', img) # Display window
    if cv2.waitKey(1) == ord('q'): # Break window
        break

vid.release()
cv2.destroyAllWindows()