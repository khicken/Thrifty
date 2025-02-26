import cv2, time
from threading import Thread
from queue import Queue

import scraper

debug = True

# img_q is str, label_q is (str, col)
img_q, label_q = Queue(), Queue()

def process_image(img_q: Queue, label_q: Queue):
    img_name = img_q.get()
    label_q.put((f'Scanning {img_name}...', (0, 255, 255)))
    name, price = scraper.scraper(img_name)
    label_q.put((f'Name: {name}, Price: {price}', (0, 255, 0)))

def main(img_q: Queue, txt_q: Queue):
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        quit(1)
    
    # frame referencing (mainly for obj detection)
    ret, ref_frame = cap.read()
    prev_frame = ref_frame # prev frame to check stationary
    out_frame = ref_frame # total output frame seen in window
    ref_set = False # if a reference has been set

    # for UI customization
    def zoom_img(val):
        global zoom
    zoom = 1.0
    width_, height_ = ref_frame.shape[:2]

    # for UI
    status_text, status_color = 'Background image not set...', (0, 0, 255)
    label_text, label_color = 'No object scanned', (0, 0, 255)
    def updateStatus(text, col=(0, 0, 255)):
        global status_text
        global status_color
        status_text, status_color = text, col
    def updateLabel(text, col=(0, 0, 255)):
        global label_text
        global label_color
        label_text, label_color = text, col

    cv2.namedWindow('Thrifty', cv2.WINDOW_AUTOSIZE)
    # cv2.createTrackbar('Zoom', 'Thrifty', zoom, 5.0, zoom_img)

    # object detection
    interval = 0.25 # intervals to run checks
    time_to_activate = 1.5 # how long objects should be stationary before scraper activation
    movement_counter = 0 # movement counter
    stationary_counter = 0 # stationary object counter
    start_time = time.time() + 3 # offset start time to give startup time
    def object_contours(frame1, frame2, out_frame) -> int:
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

    while True:
        # read camera data; frame is the original webcam feed
        ret, frame = cap.read()
        if not ret:
            print('Error: Frame could not be read.')
            cap.release()
            cv2.destroyAllWindows()
            quit(1)
        out_frame = frame # display frame is out_frame

        # object detection
        curr_time = time.time()
        if curr_time - start_time >= interval and ref_set:
            if movement_counter == 0 and stationary_counter == 0: # blank
                objects = object_contours(ref_frame, frame, out_frame)

                if objects > 0:
                    updateStatus(f'Motion detected! object_contours found: {objects}')
                    movement_counter = 1
            elif movement_counter > 0 and stationary_counter == 0: # in movement
                moving_objects = object_contours(prev_frame, frame, out_frame)
                objects = object_contours(ref_frame, frame, out_frame)
                
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
                moving_objects = object_contours(prev_frame, frame, out_frame)
                objects = object_contours(ref_frame, frame, out_frame)

                if objects > 0:
                    if moving_objects == 0:
                        stationary_counter += 1
                        updateStatus(f'Stationary object detected. Stationary counter: {stationary_counter}')

                        if stationary_counter >= time_to_activate / interval:
                            updateStatus('Scraper activated!', (0, 255, 255))
                            img_name = time.strftime("%Y-%m-%d_%H%M%S.png", time.localtime(curr_time))
                            cv2.imwrite(rf'temp\{img_name}', frame)
                            img_q.put(img_name)
                            t = Thread(name='process_image', target=process_image, args=(img_q, label_q))
                            t.start()
                            stationary_counter = 0
                    else:
                        stationary_counter = 0
                        movement_counter = 1
                        updateStatus(f'Motion detected! Stationary counter set to 0.')
                else:
                    stationary_counter = 0 # reset
            prev_frame = frame
            start_time = curr_time

        # label updating
        if label_q.qsize() > 0:
            curr_label = label_q.get()
            label_text, label_color = curr_label[0], curr_label[1]
        cv2.putText(out_frame, status_text, (10, 50), cv2.FONT_HERSHEY_COMPLEX, 1, status_color, 2)
        cv2.putText(out_frame, label_text, (10, 100), cv2.FONT_HERSHEY_COMPLEX, 1, label_color, 2)
        cv2.imshow("Thrifty", out_frame)

        # key events
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('s'):
            ref_frame = frame
            start_time = curr_time # reset for another interval
            updateLabel('Background image set!', (0, 255, 0))
            status_text = 'Background image set!'
            ref_set = True
        elif key == ord(' ') and debug: # for testing
            img_name = time.strftime("%Y-%m-%d_%H%M%S.png", time.localtime(curr_time))
            cv2.imwrite(rf'temp\{img_name}', frame)
            img_q.put(img_name)
            t = Thread(name='process_image', target=process_image, args=(img_q, label_q))
            t.start()
        elif key == ord('r'):
            ref_set = False
        elif key == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            quit()

if __name__ == '__main__':
    # m = Thread(name='main', target=main, args=(img_q, label_q))
    # m.start()
    main(img_q, label_q)