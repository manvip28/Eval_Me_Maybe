import os
from pdf2image import convert_from_path
from PIL import Image, ImageFilter

def convert_pdf_to_images(input_file, output_folder="../output/pages", poppler_path=None, dpi=500, sharpen=True):
    """
    Convert PDF pages to high-quality images.
    Returns a list of saved image file paths.
    """
    os.makedirs(output_folder, exist_ok=True)
    saved_files = []

    if input_file.lower().endswith(".pdf"):
        print(f"Converting PDF '{input_file}' to images with DPI={dpi}...")
        images = convert_from_path(input_file, dpi=dpi, poppler_path=poppler_path)
    else:
        print(f"Loading single image '{input_file}'...")
        images = [Image.open(input_file)]

    for page_idx, img in enumerate(images, start=1):
        filename = os.path.join(output_folder, f"page_{page_idx}.png")

        # Convert mode if needed
        if img.mode not in ["RGB", "L"]:
            img = img.convert("RGB")

        # Optional sharpening for thin PDF lines
        if sharpen:
            img = img.filter(ImageFilter.SHARPEN)

        # Save as high-quality PNG
        img.save(filename, "PNG", quality=100)
        saved_files.append(filename)
        print(f"Saved page {page_idx} as {filename}")

    print(f"\n[SUCCESS] Conversion complete! Total pages/images saved: {len(saved_files)}")
    return saved_files


# ====== Standalone execution ======
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python convert.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    poppler_path = r"C:\poppler-25.07.0\Library\bin"  # change as needed
    convert_pdf_to_images(input_file, poppler_path=poppler_path)
