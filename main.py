from fastapi import FastAPI, Request, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse, Response, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import List
from scripts.fileloader import archive_manager, image_verify
from scripts.ImageCheckUp import image_checkup
from scripts.report import make_report
from pathlib import Path

app = FastAPI()  

app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")
templates = Jinja2Templates(directory=Path(__file__).parent/ "templates")

current_dir = Path(__file__).parent
file_path = current_dir / "report" / "report.txt"

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(
        "index.html", 
        {"request": request}
    )

@app.post("/upload", response_class=HTMLResponse)
async def upload_files(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="Файлы не были загружены")
    
    invalid_files = []

    images = dict()

    for _file in files:
        data = await _file.read()

        if any(_file.filename.lower().endswith(ext) for ext in ['.zip', '.rar', '.7z', '.tar', '.gz']):
            arch_res = archive_manager(data, _file.filename)

            if arch_res['all_valid'] == False:
                invalid_files = invalid_files + arch_res['invalid_files']

            else:
                for img in arch_res['images_info'].keys():
                    images[img] = arch_res['images_info'][img]

        elif any(_file.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.tif', '.tiff']):
            if image_verify(data) == False:
                invalid_files.append(_file.filename)
            else:
                image_res = image_checkup(data, _file.filename, 5)
                if len(image_res.keys()) == 1:
                    raise HTTPException(status_code=400, detail=f"Ошибка обработки файла: {str(image_res['exception'])}")
                images[_file.filename] = image_res
        else:
            invalid_files.append(_file.filename)       

    suitable, unsuitable = make_report(images, file_path)



    try:
        return JSONResponse(content = {
            "all_valid": len(invalid_files) == 0,
            "valid": suitable,
            "invalid": invalid_files,
            "unsuitable": unsuitable
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download-report")
async def download_report():

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path,
        filename="report.txt",
        media_type='text/plain'
    )
    