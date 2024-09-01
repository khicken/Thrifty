import time, cv2, copy
import numpy as np
import scraper

if __name__ == '__main__':
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        quit(1)
    
    ret, ref_frame = cap.read()
    ref_set = False
    movement = 0 # counter for object to register (interval * movement = time to activate)
    start_time = time.time() + 3 # offset start time to give startup time
    interval = 1

    cv2.namedWindow('Thrifty')

    def update_threshold(val):
        global threshold_value
        threshold_value = val
    def update_threshold2(val):
        global threshold_value2
        threshold_value2 = val
    
    # Initialize the threshold value
    threshold_value = 40
    threshold_value2 = 40

    # Create a trackbar (slider) in the window to control the threshold value
    cv2.createTrackbar('Threshold (col)', 'Thrifty', threshold_value, 255, update_threshold)
    cv2.createTrackbar('Threshold (gray)', 'Thrifty', threshold_value2, 255, update_threshold2)

    def brighter(img1, img2) -> bool:
        gray1 = cv2.cvtColor(img1, cv2.COLOR_RGB2GRAY)
        gray2 = cv2.cvtColor(img2, cv2.COLOR_RGB2GRAY)
        return np.mean(gray1) > np.mean(gray2)
    
    while True:
        # read camera data
        ret, frame = cap.read()
        if not ret:
            print('Error: Frame could not be read.')
            cap.release()
            cv2.destroyAllWindows()
            quit(1)
        out_frame = frame

        # if brighter(ref_frame, frame):
        diff = cv2.absdiff(ref_frame, frame)
        # else:
            # diff = cv2.absdiff(frame, ref_frame)
        # find absolute difference
        grayed = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY) # make it grayscale
        blurred = cv2.GaussianBlur(diff, (15, 15), 0) # reduce noise and improve contour detection
        _, thresh = cv2.threshold(blurred, threshold_value, 255, cv2.THRESH_BINARY) # calc threshold
        dilated = cv2.dilate(thresh, None, iterations=3) # dilate (move pixel matrix and fill in center holes)
        grayed = cv2.cvtColor(dilated, cv2.COLOR_BGR2GRAY) # make it grayscale
        _, thresh2 = cv2.threshold(grayed, threshold_value2, 255, cv2.THRESH_BINARY) # calc threshold
        # grayed = cv2.cvtColor(dilated, cv2.COLOR_BGR2GRAY)
        # contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # print(len(contours))
        # something = False # just need to detect one anomaly
        # # draw contours
        # for contour in contours:
        #     # Ignore small contours that are not significant
        #     if cv2.contourArea(contour) < 10000:
        #         continue
        #     # Get the bounding box coordinates for the contour
        #     (x, y, w, h) = cv2.boundingRect(contour)
        #     # Draw a rectangle around the detected object
        #     cv2.rectangle(out_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        #     # Optionally, print a message or take another action
        #     print("Motion detected!")
            
            # ref_frame = copy.deepcopy(frame)
            # start_time = curr_time


        cv2.imshow("Thrifty", thresh2)

        # key events
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('s'):
            ref_frame = copy.deepcopy(frame)
            # start_time = curr_time
            ref_set = True
        if key == ord(' '):
            cv2.imwrite("temp.png", frame)
            print("estimating price...")
            time.sleep(2)
            print(f'estimated price: {scraper.scraper():.2f}')
        elif key == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            quit()