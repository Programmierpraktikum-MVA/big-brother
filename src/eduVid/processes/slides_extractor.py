import cv2
import os

def extract_slides_from_video(video_path, output_folder):
    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Load the video
    video = cv2.VideoCapture(video_path)
    if not video.isOpened():
        print("Error opening video file.")
        return

    # Initialize variables
    frame_counter = 0
    slide_counter = 0
    previous_frame = None

    # Process video frames
    while True:
        # Read the next frame
        end, frame = video.read()
        if not end:
            break

        # Skip the first frame as we need two frames for comparison
        if previous_frame is None:
            previous_frame = frame
            continue

        # Compute the absolute difference between the current and previous frames
        frame_diff = cv2.absdiff(previous_frame, frame)

        # Convert the difference to grayscale
        frame_diff_gray = cv2.cvtColor(frame_diff, cv2.COLOR_BGR2GRAY)

        # Apply thresholding to emphasize the differences
        _, thresholded_diff = cv2.threshold(frame_diff_gray, 30, 255, cv2.THRESH_BINARY)

        # Count the number of white pixels in the difference image
        num_white_pixels = cv2.countNonZero(thresholded_diff)

        # If a slide change is detected, save the previous slide as a JPG image
        if num_white_pixels > frame.shape[0] * frame.shape[1] * 0.01:
            slide_counter += 1
            slide_filename = os.path.join(output_folder, f"slide{slide_counter}.jpg")
            cv2.imwrite(slide_filename, previous_frame)

        # Update the previous frame with the current frame for the next iteration
        previous_frame = frame
        frame_counter += 1

    # Save the last slide
    slide_counter += 1
    slide_filename = os.path.join(output_folder, f"slide{slide_counter}.jpg")
    cv2.imwrite(slide_filename, previous_frame)

    # Release the video capture and print the summary
    video.release()
    print(f"Processed {frame_counter} frames. Extracted {slide_counter} slides.")

# TODO ->
#  set paths
video_path = ""
output_folder = ""
extract_slides_from_video(video_path, output_folder)
