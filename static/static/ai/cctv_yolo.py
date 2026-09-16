import argparse
import cv2

from ultralytics import YOLO


parser = argparse.ArgumentParser()

parser.add_argument(
    "--source",
    default="0",
    help="0 for webcam or path to video"
)

parser.add_argument(
    "--model",
    default="yolo11n.pt"
)

args = parser.parse_args()


source = (
    int(args.source)
    if args.source.isdigit()
    else args.source
)


model = YOLO(args.model)

cap = cv2.VideoCapture(source)


# Change these coordinates
# according to your CCTV camera.

TABLE_ZONES = [

    (1, (50, 50, 200, 160)),

    (2, (250, 50, 400, 160)),

    (3, (450, 50, 600, 160)),

    (4, (50, 220, 200, 330)),

    (5, (250, 220, 400, 330)),

    (6, (450, 220, 600, 330))

]


while True:

    success, frame = cap.read()

    if not success:
        break


    results = model(
        frame,
        classes=[0],
        verbose=False
    )[0]


    occupied = {
        table_id: False
        for table_id, zone
        in TABLE_ZONES
    }


    for box in results.boxes.xyxy.cpu().numpy():

        x1, y1, x2, y2 = (
            box.astype(int)
        )

        center_x = (
            x1 + x2
        ) // 2

        center_y = (
            y1 + y2
        ) // 2


        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            (0, 255, 0),
            2
        )


        for table_id, zone in TABLE_ZONES:

            left, top, right, bottom = zone


            if (
                left <= center_x <= right
                and
                top <= center_y <= bottom
            ):

                occupied[
                    table_id
                ] = True


    for table_id, zone in TABLE_ZONES:

        left, top, right, bottom = zone


        if occupied[table_id]:

            status = "OCCUPIED"

            color = (0, 0, 255)

        else:

            status = "FREE"

            color = (0, 200, 0)


        cv2.rectangle(
            frame,
            (left, top),
            (right, bottom),
            color,
            2
        )


        cv2.putText(
            frame,
            f"Table {table_id}: {status}",
            (left, top - 8),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            color,
            2
        )


    cv2.imshow(
        "Smart Hotel CCTV",
        frame
    )


    if cv2.waitKey(1) & 0xFF == 27:

        break


cap.release()

cv2.destroyAllWindows()
