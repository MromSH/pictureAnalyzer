import io
import zipfile
import rarfile
import py7zr
import tarfile
from fastapi import HTTPException
from PIL import Image
from .ImageCheckUp import image_checkup

def image_verify(image_bytes):
    try:
        image = Image.open(io.BytesIO(image_bytes))
        image.verify()
        return True
    except Exception as e:
        return False

def archive_manager(archive_data, archive_name):
    not_images = []
    each_image_info = dict()

    try:
        
        if archive_name.lower().endswith('.zip'):
            with zipfile.ZipFile(io.BytesIO(archive_data)) as zip_arch:
                file_list = zip_arch.filelist
                
                for _file in file_list:

                    original_filename = _file.filename
                    display_filename = original_filename

                    try:
                        display_filename = original_filename.encode('cp437').decode('utf-8')
                    except (UnicodeEncodeError, UnicodeDecodeError):
                        try:
                            display_filename = original_filename.encode('cp437').decode('cp866')
                        except:
                            try:
                                display_filename = original_filename.encode('cp850').decode('utf-8')
                            except:
                                pass

                    if not _file.is_dir():
                        try:
                            file_data = zip_arch.read(_file.filename)
                            
                            if image_verify(file_data):
                                res_image = image_checkup(file_data, display_filename, 5)
                                if len(res_image.keys()) == 1:
                                    not_images.append(display_filename)
                                else:
                                    each_image_info[display_filename] = res_image
                            else:

                                not_images.append(display_filename)
                                
                        except Exception as e:
                            not_images.append(display_filename)

        elif archive_name.lower().endswith('.rar'):
            with rarfile.RarFile(io.BytesIO(archive_data)) as rar_arch:
                file_list = rar_arch.infolist()
                
                for _file in file_list:
                    if not _file.is_dir():
                        try:
                            file_data = rar_arch.read(_file)
                            
                            if image_verify(file_data):
                                res_image = image_checkup(file_data, _file.filename, 5)
                                if len(res_image.keys()) == 1:
                                    not_images.append(_file.filename)
                                else:
                                    each_image_info[_file.filename] = res_image
                            else:
                                not_images.append(_file.filename)
                                
                        except Exception as e:
                            not_images.append(_file.filename)

        elif archive_name.lower().endswith('.7z'):
            with py7zr.SevenZipFile(io.BytesIO(archive_data), mode='r') as sz_arch:
                
                for sz_file_name, sz_file in files_dict.items():
                    try:
                        file_data = sz_file.read()
                        
                        if image_verify(file_data):
                            res_image = image_checkup(file_data, sz_file_name, 5)
                            if len(res_image.keys()) == 1:
                                not_images.append(sz_file_name)
                            else:
                                each_image_info[sz_file_name] = res_image
                        else:
                            not_images.append(sz_file_name)
                            
                    except Exception as e:
                        not_images.append(sz_file_name)

        elif archive_name.lower().endswith(('.tar', '.gz', '.tgz')):
            mode = 'r:gz' if archive_name.endswith('.gz') else 'r'
            with tarfile.open(fileobj=io.BytesIO(archive_data), mode=mode) as tar_arch:
                members = tar_arch.getmembers()
                
                for member in members:
                    if member.isfile():
                        try:
                            file_data = tar_arch.extractfile(member).read()
                            
                            if image_verify(file_data):
                                res_image = image_checkup(file_data, member.name, 5)
                                if len(res_image.keys()) == 1:
                                    not_images.append(member.name)
                                else:
                                    each_image_info[member.name] = res_image
                            else:
                                not_images.append(member.name)
                                
                        except Exception as e:
                            not_images.append(member.name)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка чтения архива: {str(e)}")

    return {
        "all_valid": len(not_images) == 0,
        "invalid_files": not_images,
        "images_info": each_image_info
    }