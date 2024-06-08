import cv2
from matplotlib import pyplot as plt

vid = cv2.VideoCapture(0)

while True:
    # Camera display stuff
    ret, frame = vid.read() # Read video

    if not ret: # Error
        print('uh oh! stinky! camera doesn\'t work.')

    cv2.imshow('here\'s the frame', frame) # Display window
    
    # Break display on q
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print(str(type(frame)))
        break

    # Image processing stuff
    img = cv2.imread(frame)


vid.release()
cv2.destroyAllWindows() 