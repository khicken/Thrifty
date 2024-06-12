import cv2

def drawLine(frame):
    cv2.line(frame, (0, 0), (100, 100), (255, 0, 0), 5)