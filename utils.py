import cv2
import numpy as np

def detect_shape(image_path):
    image = cv2.imread(image_path)
    if image is None:
        return "Image not found"

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 50, 150)

    # Tìm các contours
    contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    shape_counts = {"circle": 0, "rectangle": 0, "invalid": 0}

    for contour in contours:
        # Bỏ qua contour quá nhỏ (loại nhiễu)
        if cv2.contourArea(contour) < 1000:
            continue

        # Xác định hình dạng từ contour
        approx = cv2.approxPolyDP(contour, 0.04 * cv2.arcLength(contour, True), True)

        # Nếu có 4 đỉnh, có khả năng là banknote (hình chữ nhật)
        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = float(w) / h
            
            # Kiểm tra tỷ lệ khung hình và diện tích
            if 1.5 < aspect_ratio < 2.5 and w * h > 10000:
                shape_counts["rectangle"] += 1
            else:
                shape_counts["invalid"] += 1

        # Nếu số điểm lớn hơn 6, có khả năng là hình tròn (coin)
        elif len(approx) > 6:
            (x, y), radius = cv2.minEnclosingCircle(contour)
            circle_area = 3.14 * radius * radius
            contour_area = cv2.contourArea(contour)
            
            # So sánh diện tích hình tròn ước lượng với diện tích contour
            if 0.8 < contour_area / circle_area < 1.2:
                shape_counts["circle"] += 1
            else:
                shape_counts["invalid"] += 1
        else:
            shape_counts["invalid"] += 1

    # Đưa ra kết quả dựa trên số lượng đối tượng phát hiện được
    if shape_counts["circle"] > 0 and shape_counts["rectangle"] == 0:
        return "coin"
    elif shape_counts["rectangle"] > 0 and shape_counts["circle"] == 0:
        return "banknote"
    elif shape_counts["circle"] > 0 and shape_counts["rectangle"] > 0:
        return "invalid"  # Hỗn hợp, không hợp lệ
    else:
        return "unknown"
