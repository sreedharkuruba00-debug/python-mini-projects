import cv2
from ultralytics import YOLO

# Load YOLO AI model
model = YOLO("yolo11n.pt")

# Open CCTV/webcam
# 0 = laptop webcam
camera = cv2.VideoCapture(0)

while True:

    # Read camera frame
    success, frame = camera.read()

    if not success:
        print("Camera not found")
        break

    # Detect people
    results = model(
        frame,
        classes=[0],
        verbose=False
    )

    # Number of people detected
    people = len(results[0].boxes)

    # Show detection on screen
    frame = results[0].plot()

    # Display number of people
    cv2.putText(
        frame,
        "People detected: " + str(people),
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    # Show CCTV window
    cv2.imshow(
        "Smart Hotel CCTV",
        frame
    )

    # Press Q to stop
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


camera.release()
cv2.destroyAllWindows()
