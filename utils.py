import cv2
import numpy as np

def detect_shape(image_path):
    image = cv2.imread(image_path)
    if image is None:
        return "Image not found"

    # Chuyển đổi sang grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cv2.imwrite('debug_gray.png', gray)

    # Làm mờ ảnh bằng Gaussian Blur
    blurred = cv2.GaussianBlur(gray, (9, 9), 2)
    cv2.imwrite('debug_blurred.png', blurred)

    # Phát hiện biên với bộ lọc Canny
    edged = cv2.Canny(blurred, 30, 150)
    cv2.imwrite('debug_edged.png', edged)

    # Tìm các đường viền
    contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Đếm hình dạng
    shape_counts = {"circle": 0, "rectangle": 0, "invalid": 0}
    log_messages = []

    for contour in contours:
        # Bỏ qua các vùng nhiễu nhỏ
        if cv2.contourArea(contour) < 500:
            continue

        # Xấp xỉ đa giác
        approx = cv2.approxPolyDP(contour, 0.04 * cv2.arcLength(contour, True), True)

        # 🟩 Kiểm tra hình chữ nhật
        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = float(w) / h
            if 0.8 < aspect_ratio < 1.2:
                shape_counts["rectangle"] += 1
                cv2.drawContours(image, [approx], -1, (0, 255, 0), 3)
            else:
                shape_counts["invalid"] += 1

        # 🔵 Kiểm tra hình tròn với HoughCircles
        else:
            circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, 1, 20,
                                       param1=50, param2=30, minRadius=1, maxRadius=40)

            if circles is not None:
                circles = np.uint16(np.around(circles))
                for i in circles[0, :]:
                    # Tâm và bán kính
                    center = (i[0], i[1])
                    radius = i[2]

                    # Vẽ hình tròn và tâm
                    cv2.circle(image, center, radius, (255, 0, 0), 3)
                    cv2.circle(image, center, 3, (0, 0, 255), -1)

                    # Đánh dấu hình tròn
                    shape_counts["circle"] += 1
            else:
                shape_counts["invalid"] += 1

    # Lưu thông tin log vào file
    with open("shape_detection_log.txt", "w") as log_file:
        for msg in log_messages:
            log_file.write(msg + "\n")

    # Lưu kết quả ảnh sau khi đánh dấu
    cv2.imwrite('debug_final_image.png', image)

    # Đưa ra kết quả
    if shape_counts["circle"] > 0 and shape_counts["rectangle"] == 0:
        return "coin"
    elif shape_counts["rectangle"] > 0 and shape_counts["circle"] == 0:
        return "banknote"
    elif shape_counts["circle"] > 0 and shape_counts["rectangle"] > 0:
        return "invalid"
    else:
        return "unknown"
