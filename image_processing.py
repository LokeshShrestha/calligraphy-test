import cv2 as cv
import numpy as np
import os

# --- Read image ---
img = cv.imread(os.path.join(".", "Photos", "dha.png"))
if img is None:
    print("Error: Image not found!")
    exit()

# Convert to grayscale
img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

# --- Threshold: white letter on black background ---
_, thresh = cv.threshold(img_gray, 0, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)

# --- Optional clean-up: remove tiny dots or gaps (this is where boldness control happens) ---
kernel = np.ones((2, 2), np.uint8)  # Adjust kernel size for erosion control
thresh = cv.erode(thresh, kernel, iterations=1)  # Erosion instead of closing to preserve contour details

# --- Find contours ---
contours, _ = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
if not contours:
    print("No contours found.")
    exit()

# --- Filter out very small areas (noise) ---
filtered = [c for c in contours if cv.contourArea(c) > 100]  # Adjust 100 if needed
if not filtered:
    print("No significant contours found.")
    exit()

# --- Selective merging: keep contours that are near the largest one ---
main_contour = max(filtered, key=cv.contourArea)
x_main, y_main, w_main, h_main = cv.boundingRect(main_contour)
main_box = np.array([x_main, y_main, x_main + w_main, y_main + h_main])

close_contours = [main_contour]

for cnt in filtered:
    if cnt is main_contour:
        continue
    x, y, w, h = cv.boundingRect(cnt)
    # Compute overlap or closeness
    if not (x + w < main_box[0] - 10 or x > main_box[2] + 10 or
            y + h < main_box[1] - 10 or y > main_box[3] + 10):
        close_contours.append(cnt)

# --- Merge selected contours ---
all_points = np.vstack(close_contours)

# --- Get bounding box around merged contours ---
x, y, w, h = cv.boundingRect(all_points)

# --- Visualize the bounding box on the threshold image ---
img_box = cv.cvtColor(thresh, cv.COLOR_GRAY2BGR)
cv.rectangle(img_box, (x, y), (x + w, y + h), (0, 255, 0), 2)

# --- Crop the region ---
cropped = thresh[y:y+h, x:x+w]

# --- Center the cropped region in a square ---
side = max(w, h)
square = np.zeros((side, side), dtype=np.uint8)
start_x = (side - w) // 2
start_y = (side - h) // 2
square[start_y:start_y+h, start_x:start_x+w] = cropped

# --- Resize to 64x64 ---
resized = cv.resize(square, (64, 64), interpolation=cv.INTER_AREA)

# --- Create output folder if it doesn't exist ---
output_folder = "cropped_words"
os.makedirs(output_folder, exist_ok=True)

# --- Find the next available filename ---
existing_files = os.listdir(output_folder)
file_index = 0
while f"cropped_image_{file_index}.png" in existing_files:
    file_index += 1

# --- Save the cropped image with the new filename ---
output_filename = os.path.join(output_folder, f"cropped_image_{file_index}.png")
cv.imwrite(output_filename, resized)

# --- Debugging/Visualizations ---
cv.imshow("Threshold", thresh)
cv.imshow("Bounding Box", img_box)
cv.imshow("Cropped", cropped)
cv.imshow("Centered & Resized (64x64)", resized)
cv.waitKey(0)
cv.destroyAllWindows()
