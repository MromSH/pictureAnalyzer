def make_report(image_data, report_path):
    suitable = []
    unsuitable = []

    if len(image_data.keys()) > 0:
        with open(report_path, "w", encoding="utf-8") as f:
            for image_name in image_data.keys():
                if image_data[image_name]["is_ok"] == True:
                    f.write(f"Изображение {image_name} подходит для типографии\n")
                    f.write(f"Размер в МБ: {image_data[image_name]['size_Mb']}\n")
                    f.write(f"Цветовой мод: {image_data[image_name]['mode']}\n")
                    f.write(f"Размеры: {image_data[image_name]['image_width_mm']}x{image_data[image_name]['image_height_mm']} мм\n")
                    f.write(f"DPI: {image_data[image_name]['dpi']}\n\n")

                    suitable.append(image_name)
                else:
                    errors = []
                    f.write(f"Изображение {image_name} не подходит для типографии\n")
                    f.write(f"Размер в МБ: {image_data[image_name]['size_Mb']}\n")
                    f.write(f"Цветовой мод: {image_data[image_name]['mode']}\n")
                    f.write(f"Размеры: {image_data[image_name]['image_width_mm']}x{image_data[image_name]['image_height_mm']} мм\n")
                    f.write(f"DPI: {image_data[image_name]['dpi']}\n")

                    f.write("Проблемы в изображении:\n")
                    if image_data[image_name]['mode'] != 'CMYK':
                        f.write(f"Цветовой мод в изображении: {image_data[image_name]['mode']} | ТРЕБУЕТСЯ: CMYK\n")
                        errors.append(f"Цветовой мод в изображении: {image_data[image_name]['mode']} | ТРЕБУЕТСЯ: CMYK")
                    if image_data[image_name]['size_Mb'] > 100:
                        f.write(f"Размер изображения в МБ: {image_data[image_name]['size_Mb']} | ТРЕБУЕТСЯ: не более 100МБ\n")
                        errors.append(f"Размер изображения в МБ: {image_data[image_name]['size_Mb']} | ТРЕБУЕТСЯ: не более 100МБ")
                    if image_data[image_name]['image_width_mm'] > 110 or image_data[image_name]['image_width_mm'] < 100 or image_data[image_name]['image_height_mm'] > 80 or image_data[image_name]['image_height_mm'] < 70:
                        f.write(f"Размеры изображения в мм: {image_data[image_name]['image_width_mm']}x{image_data[image_name]['image_height_mm']} мм | ТРЕБУЕТСЯ: ширина - от 100 до 110 мм, высота - от 70 до 80 мм\n")
                        errors.append(f"Размеры изображения в мм: {image_data[image_name]['image_width_mm']}x{image_data[image_name]['image_height_mm']} мм | ТРЕБУЕТСЯ: ширина - от 100 до 110 мм, высота - от 70 до 80 мм")
                    if len(image_data[image_name]['text_info']) > 0:
                        f.write(f"В изображении следующий текст выходит за ограничения: {' | '.join(image_data[image_name]['text_info'])}\n")
                        errors.append(f"В изображении следующий текст выходит за ограничения: {' | '.join(image_data[image_name]['text_info'])}")
                    f.write("\n")

                    unsuitable.append({image_name: errors})
    
    return suitable, unsuitable
