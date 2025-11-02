import os
import json
import requests
import time
from PIL import Image
import numpy as np
import cv2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def extract_json(input_image, azure_endpoint=None, azure_key=None, output_folder="../output"):
    """
    Extract diagrams from a single image using Azure Document Intelligence.
    Returns a dictionary with text and diagram info.
    """
    # Get Azure credentials from environment or parameters
    azure_endpoint = azure_endpoint or os.getenv("AZURE_AI_VISION_ENDPOINT")
    azure_key = azure_key or os.getenv("AZURE_AI_VISION_KEY")
    
    if not azure_endpoint or not azure_key:
        raise ValueError("Azure AI Vision credentials not found. Please set AZURE_AI_VISION_ENDPOINT and AZURE_AI_VISION_KEY in .env file or pass as parameters.")
    
    os.makedirs(os.path.join(output_folder, "diagrams"), exist_ok=True)

    print(f"[INFO] Extracting text positions from {input_image}...")
    url = f"{azure_endpoint}/documentintelligence/documentModels/prebuilt-read:analyze?api-version=2024-11-30"

    with open(input_image, "rb") as f:
        file_data = f.read()

    headers = {"Ocp-Apim-Subscription-Key": azure_key, "Content-Type": "application/octet-stream"}
    response = requests.post(url, headers=headers, data=file_data)
    response.raise_for_status()
    operation_url = response.headers["Operation-Location"]

    while True:
        result = requests.get(operation_url, headers={"Ocp-Apim-Subscription-Key": azure_key}).json()
        if result.get("status") == "succeeded":
            break
        time.sleep(2)

    img = Image.open(input_image)
    img_cv = cv2.imread(input_image)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    img_width, img_height = img.size

    text_lines = []
    all_text_regions = []
    for page in result["analyzeResult"].get("pages", []):
        for line in page.get("lines", []):
            content = line.get("content", "")
            polygon = line.get("polygon", [])
            if len(polygon) >= 8:
                xs = [polygon[i] for i in range(0, len(polygon), 2)]
                ys = [polygon[i] for i in range(1, len(polygon), 2)]
                box = {"text": content, "x1": int(min(xs)), "y1": int(min(ys)), "x2": int(max(xs)), "y2": int(max(ys))}
                all_text_regions.append(box)
                text_lines.append(content)

    text_mask = np.ones(gray.shape, dtype=np.uint8) * 255
    for text_box in all_text_regions:
        padding = 15
        x1 = max(0, text_box["x1"] - padding)
        y1 = max(0, text_box["y1"] - padding)
        x2 = min(img_width, text_box["x2"] + padding)
        y2 = min(img_height, text_box["y2"] + padding)
        text_mask[y1:y2, x1:x2] = 0

    _, binary = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
    non_text_ink = cv2.bitwise_and(binary, text_mask)
    kernel = np.ones((3, 3), np.uint8)
    closed = cv2.morphologyEx(non_text_ink, cv2.MORPH_CLOSE, kernel, iterations=2)
    dilated = cv2.dilate(closed, kernel, iterations=1)

    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    diagrams = []

    MIN_AREA = 2000; MAX_AREA = 100000; MIN_DENSITY = 0.03; MAX_DENSITY = 0.6
    MIN_WIDTH = 80; MIN_HEIGHT = 80; MAX_WIDTH = 500; MAX_HEIGHT = 400

    for contour in contours:
        area = cv2.contourArea(contour)
        if MIN_AREA < area < MAX_AREA:
            x, y, w, h = cv2.boundingRect(contour)
            if w < MIN_WIDTH or h < MIN_HEIGHT or w > MAX_WIDTH or h > MAX_HEIGHT: continue
            aspect_ratio = min(w, h) / max(w, h) if max(w, h) > 0 else 0
            if aspect_ratio < 0.2: continue
            roi = non_text_ink[y:y+h, x:x+w]
            if roi.size > 0:
                density = np.sum(roi > 0) / roi.size
                if MIN_DENSITY < density < MAX_DENSITY:
                    diagram_y_center = y + h // 2
                    closest_q = "Unknown"; min_distance = float('inf')
                    for text_box in all_text_regions:
                        text = text_box["text"].strip()
                        if text.startswith("Q"):
                            q_y = text_box["y1"]
                            distance = abs(diagram_y_center - q_y)
                            if 0 < (diagram_y_center - q_y) < 400 and distance < min_distance:
                                min_distance = distance
                                closest_q = text
                    padding = 20
                    x1 = max(0, x - padding); y1 = max(0, y - padding)
                    x2 = min(img_width, x + w + padding); y2 = min(img_height, y + h + padding)
                    cropped = img.crop((x1, y1, x2, y2))
                    filename = os.path.join(output_folder, "diagrams", f"diagram_{len(diagrams)+1}_{closest_q.replace('.', '').replace(' ', '_')}.png")
                    if cropped.mode == 'RGBA': cropped = cropped.convert('RGB')
                    cropped.save(filename)
                    diagrams.append({"filename": filename, "coordinates": (x1, y1, x2, y2), "question": closest_q, "area": int(area), "density": round(density,3), "dimensions": f"{w}x{h}", "aspect_ratio": round(aspect_ratio,2)})
                    print(f"[DIAGRAM] Diagram {len(diagrams)}: {filename} | Question: {closest_q}")

    output_data = {"text": "\n".join(text_lines), "text_line_count": len(text_lines), "diagrams": diagrams, "total_diagrams": len(diagrams)}
    with open(os.path.join(output_folder, "structured_output.json"), "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"\n[SUCCESS] Extraction complete! Text lines: {len(text_lines)}, Diagrams: {len(diagrams)}")
    return output_data
