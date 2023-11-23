import io
import re


from pdf2image import convert_from_path
import pytesseract


# 指定 Tesseract.exe 的路径，本地已经设置则不需要
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def ocr_scan_pdf(pdf_path):
    # 从 PDF 转换图片
    images = convert_from_path(pdf_path)

    for i in range(len(images)):
        # 进行 OCR
        text = pytesseract.image_to_string(images[i], lang='chi_sim')  # 如果是英文，lang='eng'
        # text = pytesseract.image_to_string(images[i], lang='eng')
        text = re.sub(' ', '', text)
        text = re.sub('\n', '', text)
        print(f"Page {i + 1} Text: {text}")


pdf_path = "./扫描件/2.pdf"
ocr_scan_pdf(pdf_path)
