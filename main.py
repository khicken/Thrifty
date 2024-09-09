import cv2, time, multiprocessing
import scraper

debug = True

def worker(queue):
    out = scraper.scraper()
    queue.put(out)

if __name__ == '__main__':
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        quit(1)
    
    ret, ref_frame = cap.read()
    prev_frame = ref_frame # prev frame to check stationary
    out_frame = ref_frame # total output frame seen in window

    # for object detection
    ref_set = False # if a reference has been set
    movement_counter = 0 # movement counter
    stationary_counter = 0 # stationary object counter
    time_to_activate = 1.5 # activate scraper when object is in frame for this long
    scraping = False # is the scraper running?

    start_time = time.time() + 3 # offset start time to give startup time
    interval = 0.25 # intervals to run checks

    # for customization
    def zoom_img(val):
        global zoom
    zoom = 1.0
    width_, height_ = ref_frame.shape[:2]

    # for UI

    def updateStatus(text, col=(0, 0, 255)):
        global status_text
        status_text = text
        global status_color
        status_color = col
    def updateLabel(text, col=(0, 0, 255)):
        global label_text
        label_text = text
        global label_color
        label_color = col
    status_text = 'Background image not set'
    status_color = (0, 0, 255)
    label_text = 'No object scanned'
    label_color = (0, 0, 255)
    cv2.namedWindow('Thrifty', cv2.WINDOW_AUTOSIZE)
    # cv2.createTrackbar('Zoom', 'Thrifty', zoom, 5.0, zoom_img)

    # object detection
    def contours(frame1, frame2, out_frame) -> int:
        diff = cv2.absdiff(frame1, frame2) # find absolute difference
        grayed = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY) # make it grayscale
        blurred = cv2.GaussianBlur(grayed, (7, 7), 0) # reduce noise and improve contour detection
        _, thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY) # calc threshold
        dilated = cv2.dilate(thresh, None, iterations=3) # dilate (move pixel matrix and fill in center holes)
        contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        if debug:
            out_frame = dilated
        
        out = 0
        for contour in contours:
            if cv2.contourArea(contour) < 10000:
                continue
            (x, y, w, h) = cv2.boundingRect(contour)
            cv2.rectangle(out_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            out += 1
        return out
    
    # processes
    scraping = False

    while True:
        # read camera data; frame is the original webcam feed
        ret, frame = cap.read()
        if not ret:
            print('Error: Frame could not be read.')
            cap.release()
            cv2.destroyAllWindows()
            quit(1)
        
        out_frame = frame

        # object detection
        curr_time = time.time()
        if curr_time - start_time >= interval and ref_set:
            if movement_counter == 0 and stationary_counter == 0: # blank
                objects = contours(ref_frame, frame, out_frame)

                if objects > 0:

                    updateStatus(f'Motion detected! Contours found: {objects}')
                    movement_counter = 1
            elif movement_counter > 0 and stationary_counter == 0: # in movement
                moving_objects = contours(prev_frame, frame, out_frame)
                objects = contours(ref_frame, frame, out_frame)
                
                if objects > 0:
                    if moving_objects > 0:
                        movement_counter += 1
                        updateStatus(f'Motion continually detected. Movement counter: {movement_counter}')
                    else:
                        updateStatus('Motion no longer detected. Movement counter set to 0.')
                        movement_counter = 0
                        stationary_counter = 1
                else:
                    movement_counter = 0
            elif movement_counter == 0 and stationary_counter > 0: # was moving, now stationary
                moving_objects = contours(prev_frame, frame, out_frame)
                objects = contours(ref_frame, frame, out_frame)

                if objects > 0:
                    if moving_objects == 0:
                        stationary_counter += 1
                        updateStatus(f'Stationary object detected. Stationary counter: {stationary_counter}')

                        if stationary_counter >= time_to_activate / interval and not scraping:
                            scraping = True
                            updateStatus('Scraper activated. Scanning in progress...', (0, 255, 255))
                            cv2.imwrite("temp.png", frame)

                            # # multiprocessing
                            # queue = multiprocessing.Queue()
                            # process = multiprocessing.Process(target=worker, args=(queue,))
                            # process.start()
                            # result = queue.get() # waits for result to be available

                            # output
                            label_text = f'Estimate price: {scraper.scraper():.2f}'
                            scraping = False
                    else:
                        stationary_counter = 0
                        movement_counter = 1
                        updateStatus(f'Motion detected! Stationary counter set to 0.')
                else:
                    stationary_counter = 0 # reset
            prev_frame = frame
            start_time = curr_time

        cv2.putText(out_frame, status_text, (10, 10), cv2.FONT_HERSHEY_COMPLEX, 1, status_color, 2)
        cv2.putText(out_frame, label_text, (10, 50), cv2.FONT_HERSHEY_COMPLEX, 1, status_color, 2)
        cv2.imshow("Thrifty", out_frame)

        # key events
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('s'):
            ref_frame = frame
            start_time = curr_time # reset for another interval
            ref_set = True
        elif key == ord(' '):
            cv2.imwrite("temp.png", frame)
            print("estimating price...")
            time.sleep(2)
            print(f'estimated price: {scraper.scraper():.2f}')
        elif key == ord('r'):
            ref_set = False
        elif key == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            quit()