import time, cv2, copy
import random, os
import numpy as np
import scraper


from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

def camTest():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        quit(1)
    
    ret, ref_frame = cap.read()
    ref_frame_hsv = cv2.cvtColor(ref_frame, cv2.COLOR_BGR2HSV)
    ref_set = False
    movement = 0 # counter for object to register (interval * movement = time to activate)
    start_time = time.time() + 3 # offset start time to give startup time
    interval = 1

    cv2.namedWindow('Thrifty', cv2.WINDOW_AUTOSIZE)

    height, width, _ = ref_frame.shape
    grid_image = np.zeros((height * 2, width * 2, 3), dtype=np.uint8)

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
    
    fgbg = cv2.createBackgroundSubtractorMOG2(detectShadows=True)

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
        diff = cv2.absdiff(ref_frame, frame) # find absolute difference
        grayed = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY) # make it grayscale
        blurred = cv2.GaussianBlur(grayed, (7, 7), 0) # reduce noise and improve contour detection
        _, thresh = cv2.threshold(blurred, threshold_value, 255, cv2.THRESH_BINARY) # calc threshold
        dilated = cv2.dilate(thresh, None, iterations=3) # dilate (move pixel matrix and fill in center holes)

        # shadow removal method 1
        fgmask = fgbg.apply(frame) # apply subtraction
        _, fgmask = cv2.threshold(fgmask, 220, 255, cv2.THRESH_BINARY) # remove shadows

        # shadow removal method 2
        frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV) # convert current frame to hsv
        diff = cv2.absdiff(ref_frame_hsv, frame_hsv) # find abs diff
        h, s, v = cv2.split(diff) # split HSV channels
        _, thresh_s = cv2.threshold(s, threshold_value, 255, cv2.THRESH_BINARY) # set threshold on S channel
        _, thresh_v = cv2.threshold(v, threshold_value, 255, cv2.THRESH_BINARY) # set threshold on V channel
        motion_mask = cv2.bitwise_or(thresh_s, thresh_v) # combine thresholds to get mask

        moving_objects = cv2.bitwise_and(frame, frame, mask=motion_mask)

        # concat views as grid
        frame2 = cv2.cvtColor(motion_mask, cv2.COLOR_GRAY2BGR)
        frame3 = cv2.cvtColor(dilated, cv2.COLOR_GRAY2BGR)
        frame4 = cv2.cvtColor(fgmask, cv2.COLOR_GRAY2BGR)
        grid_image[0:height, 0:width] = cv2.resize(moving_objects, (width, height))          # Top-left
        grid_image[0:height, width:width*2] = cv2.resize(frame2, (width, height)) # Top-right
        grid_image[height:height*2, 0:width] = cv2.resize(frame3, (width, height)) # Bottom-left
        grid_image[height:height*2, width:width*2] = cv2.resize(frame4, (width, height)) # Bottom-right
        cv2.imshow("Thrifty", grid_image)

        # key events
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('s'):
            ref_frame = copy.deepcopy(frame)
            ref_frame_hsv = cv2.cvtColor(ref_frame, cv2.COLOR_BGR2HSV)
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

def scraperTest():
    # create window
        service = Service('./chromedriver.exe')
        options = webdriver.ChromeOptions()
        options.binary_location = './chrome-win64/chrome.exe'
        #options.add_argument('--headless') # need to fix this later, will have to remove pyautogui
        browser = webdriver.Chrome(service=service, options=options)

        # boot into google.com like a regular human
        browser.maximize_window()
        browser.implicitly_wait(4)
        browser.get("https://www.google.com/")

        # make the google lens search
        browser.implicitly_wait(random.uniform(0.5, 2.0))
        browser.find_element(By.CLASS_NAME, 'nDcEnd').click() # click lens button
        browser.implicitly_wait(random.uniform(0.5, 2.0))
        hm = browser.find_element(By.CLASS_NAME, 'DV7the').click() # click upload image button
        
        browser.execute_script("""
        var input = document.createElement('input');
        input.type = 'file';
        input.style.display = 'block';
        document.body.appendChild(input);
        input.onchange = function() {
            var file = input.files[0];
            console.log('File selected:', file.name);
        };
        input.click();
        """)
        time.sleep(2)
        file_input = browser.find_element(By.XPATH, '//input[@type="file"]')
        file_input.send_keys(os.getcwd() + fr'\test.png')  # Change this to the path of your image file
        time.sleep(10)
        print(browser.page_source)

x = 10
def funcTest(y):
    y = 100
# x = 3
if __name__ == '__main__':
    camTest()