import time, cv2
import scraper

# main file, opens camera and performs stuff

if __name__ == '__main__':
    # open capture
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        quit(1)

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Error: Could not read frame from webcam.")
            quit(1)

        cv2.imshow("Camera", frame)

        key = cv2.waitKey(1)

        if key == ord('s'):
            cv2.imwrite("temp.png", frame)
            print("Image saved as 'temp.png'")
            time.sleep(2)
            print(f'estimated price: {scraper.scraper():.2f}')
        elif key == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            quit()