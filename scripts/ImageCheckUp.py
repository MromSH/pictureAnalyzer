from PIL import Image
import io
import math
import cv2
import numpy as np
from paddleocr import PaddleOCR
from typing import Dict, List


def image_info(image_bytes, image_name):
    try:
        image = Image.open(io.BytesIO(image_bytes))
        image_size_Mb = len(image_bytes) / (1024 * 1024)
        image_color_space = image.mode

        image_dpi = (0, 0)

        if image_name.lower().endswith('.tiff'):
            exif_data = image.getexif()
            
            if exif_data:
                x_resol = exif_data.get(282)
                y_resol = exif_data.get(283)
                resol_unit = exif_data.get(296)

                if x_resol and y_resol:
                    x_dpi = float(x_resol)
                    y_dpi = float(y_resol)
                            
                    if resol_unit:
                        unit = float(resol_unit)
                        if unit == 3:
                            x_dpi = x_dpi * 2.54
                            y_dpi = y_dpi * 2.54
                            
                    image_dpi = (x_dpi, y_dpi)
                else:
                    image_dpi = (300, 300)
            else:
                image_dpi = (300, 300)
        else:
            image_dpi = image.info.get('dpi', (300, 300))

        image_width_px, image_height_px = image.size

        image_width_mm = round((image_width_px / image_dpi[0]) * 25.4)
        image_height_mm = round((image_height_px / image_dpi[1]) * 25.4)

        image_info = {
            "size_Mb": image_size_Mb,
            "mode": image_color_space,
            "image_width_mm": image_width_mm,
            "image_height_mm": image_height_mm,
            "image_width_px": image_width_px,
            "image_height_px": image_height_px,
            "dpi": image_dpi
        }

        return image_info

    except Exception as error:
            return {"exception": error}


def text_extracting(image_bytes):
    pil_image = Image.open(io.BytesIO(image_bytes))
    image = np.array(pil_image)


    if len(image.shape) == 3 and image.shape[2] == 4:
        image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
    elif len(image.shape) == 2:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)


    ocr = PaddleOCR(use_angle_cls=False)
    result = ocr.ocr(image)

    if not result or not isinstance(result, list) or len(result) == 0:
        return {"is_any_text": False}
    
    data = result[0]
    text_detected = data.get('rec_texts', [])
    scores = data.get('rec_scores', [])
    coordinates = data.get('rec_polys', data.get('dt_polys', []))

    result_text_with_coords = {"is_any_text": False}
    
    for i in range(len((text_detected))):
        text = text_detected[i]
        if text and isinstance(text, str) and text.strip():
            confidence = scores[i]
            coords = coordinates[i]

            if confidence > 0.5:
                result_text_with_coords[text] = coords
                result_text_with_coords["is_any_text"] = True
    
    return result_text_with_coords


def text_checking(image_bytes, image_dpi, indent_mm, image_width_px, image_height_px):
    try:

        vertical_indent_px = (image_dpi[1] * indent_mm) / 25.4
        horizontal_indent_px = (image_dpi[0] * indent_mm) / 25.4

        standart_image_width_px = (image_dpi[0] * 100) / 25.4
        standart_image_height_px = (image_dpi[1] * 70) / 25.4

        real_outer_width_indent_px = (image_width_px - standart_image_width_px) / 2
        real_outer_height_indent_px = (image_height_px - standart_image_height_px) / 2

        text = text_extracting(image_bytes)

        unsuitable_text = []

        if text['is_any_text'] == True:
            for txt in text.keys():
                if txt != 'is_any_text':
                    upper_left_corner = text[txt][0]
                    lower_right_corner = text[txt][2]

                    if upper_left_corner[0] < real_outer_width_indent_px + horizontal_indent_px:
                        unsuitable_text.append(txt)
                        continue
                    if upper_left_corner[1] < real_outer_height_indent_px + vertical_indent_px:
                        unsuitable_text.append(txt)
                        continue
                    if lower_right_corner[0] > image_width_px - real_outer_width_indent_px - horizontal_indent_px:
                        unsuitable_text.append(txt)
                        continue
                    if lower_right_corner[1] > image_height_px - real_outer_height_indent_px - vertical_indent_px:
                        unsuitable_text.append(txt)
                        continue
              
        return {
            "is_ok": len(unsuitable_text) == 0,
            "unsuitable_text": unsuitable_text
        }       

    except Exception as error:
        return {'exception': str(error) + "indinda"}


def image_checkup(image_bytes, image_name, indent_mm):    

    img_info = image_info(image_bytes, image_name)   
    if len(img_info.keys()) == 1:
        return img_info
    
    text_info = text_checking(image_bytes, img_info['dpi'], indent_mm, img_info['image_width_px'], img_info['image_height_px'])
    if len(text_info.keys()) == 1:
        return text_info
    
    suitable_im = True
    report_data = dict()

    if img_info['size_Mb'] > 100:
        suitable_im = False
    if img_info['mode'] != 'CMYK':
        suitable_im = False
    if img_info['image_width_mm'] > 110 or img_info['image_width_mm'] < 100:
        suitable_im = False
    if img_info['image_height_mm'] > 80 or img_info['image_height_mm'] < 70:
        suitable_im = False
    if min(img_info['dpi']) < 300:
        suitable_im = False
    if text_info['is_ok'] == False:
        suitable_im = False

    if suitable_im == False:
        report_data["is_ok"] = False
    else:
        report_data["is_ok"] = True

    report_data['size_Mb'] = img_info['size_Mb']
    report_data['mode'] = img_info['mode']
    report_data['image_width_mm'] = img_info['image_width_mm']
    report_data['image_height_mm'] = img_info['image_height_mm']
    report_data['dpi'] = img_info['dpi']
    report_data['text_info'] = text_info['unsuitable_text']
    
    return report_data

