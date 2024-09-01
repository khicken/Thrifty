import time, cv2, copy
import scraper

debug = True

if __name__ == '__main__':
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        quit(1)
    
    ret, ref_frame = cap.read()
    out_frame = ref_frame
    ref_set = False
    movement = 0 # counter for object to register (interval * movement = time to activate)
    start_time = time.time() + 3 # offset start time to give startup time
    interval = 1

    cv2.namedWindow('Thrifty', cv2.WINDOW_AUTOSIZE)

    while True:
        # read camera data
        ret, frame = cap.read()
        if not ret:
            print('Error: Frame could not be read.')
            cap.release()
            cv2.destroyAllWindows()
            quit(1)
        
        if not debug:
            out_frame = frame

        # object detection
        curr_time = time.time()
        if curr_time - start_time >= interval and ref_set:
            if movement < 4:
                diff = cv2.absdiff(ref_frame, frame) # find absolute difference
                grayed = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY) # make it grayscale
                blurred = cv2.GaussianBlur(grayed, (7, 7), 0) # reduce noise and improve contour detection
                _, thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY) # calc threshold
                dilated = cv2.dilate(thresh, None, iterations=3) # dilate (move pixel matrix and fill in center holes)
                contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                print(len(contours))
                something = False # just need to detect one anomaly
                out_frame = dilated
                # draw contours
                for contour in contours:
                    # Ignore small contours that are not significant
                    if cv2.contourArea(contour) < 10000:
                        continue
                    # Get the bounding box coordinates for the contour
                    (x, y, w, h) = cv2.boundingRect(contour)
                    # Draw a rectangle around the detected object
                    cv2.rectangle(out_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    # Optionally, print a message or take another action
                    print("Motion detected!")
                    something = True
                    break

                if something:
                    print("Movement counter: ".join(str(movement)))
                    movement += 1
                else:
                    print(f'movement reset to 0')
                    movement = 0
            else:
                print('ESTIMATE PRICE HEERRRRREEEEEEEEE')
                movement = 0
            
            # ref_frame = copy.deepcopy(frame)
            start_time = curr_time


        cv2.imshow("Thrifty", out_frame)

        # key events
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('s'):
            ref_frame = copy.deepcopy(frame)
            start_time = curr_time
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