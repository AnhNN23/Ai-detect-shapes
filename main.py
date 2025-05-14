from fastapi import FastAPI, File, UploadFile, HTTPException
from utils import detect_shape
import os
from fastapi.responses import JSONResponse

app = FastAPI()

# Đảm bảo thư mục lưu trữ file tạm thời tồn tại
os.makedirs("temp", exist_ok=True)

def generate_response(status: int, message: str, shape: str = None):
    response = {
        "status": status,
        "message": message
    }
    if shape:
        response["shape"] = shape
    return JSONResponse(content=response, status_code=status)

@app.post("/detect")
async def detect_shape_api(file: UploadFile = File(...)):
    file_location = f"temp/{file.filename}"
    
    try:
        # Ghi file được upload vào thư mục tạm
        with open(file_location, "wb") as buffer:
            buffer.write(await file.read())

        # Gọi hàm nhận diện hình dạng
        shape = detect_shape(file_location)

        # Xóa file tạm sau khi xử lý xong
        os.remove(file_location)

        if shape == "Image not found":
            raise HTTPException(status_code=404, detail="Image not found")

        shape_mapping = {
            "coin": "Coin detected",
            "banknote": "Banknote detected",
            "invalid": "Invalid combination of shapes",
            "unknown": "No recognizable shapes found"
        }

        message = shape_mapping.get(shape, "Unexpected error")
        return generate_response(200, message, shape)

    except Exception as e:
        # Đảm bảo xóa file nếu có lỗi
        if os.path.exists(file_location):
            os.remove(file_location)
        return generate_response(500, f"Internal server error: {str(e)}")
