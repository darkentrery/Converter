import io
import os
import subprocess
import tempfile
from pathlib import Path

import pandas as pd
import pdfkit
from PIL import Image

from app import entity
from app.config import config
from app.repository.sqlalchemy import SAUnitOfWork


class ConverterService:
    def __init__(self, uow: SAUnitOfWork):
        self.uow = uow

    async def from_jpg_to_pdf(self, orientation: str, images: list[bytes]) -> io.BytesIO:
        images = [self.resize_to_a4(Image.open(io.BytesIO(img)).convert("RGB"), orientation) for img in images]
        pdf_bytes = io.BytesIO()
        images[0].save(pdf_bytes, format="PDF", save_all=True, append_images=images[1:])
        pdf_bytes.seek(0)
        return pdf_bytes

    def resize_to_a4(self, image: Image.Image, orientation: str) -> Image.Image:
        """Масштабирует изображение под размер A4, сохраняя пропорции."""
        orientation = orientation if orientation in [entity.Orientation.PORTRAIT.value,
                                                     entity.Orientation.LANDSCAPE.value] else self.get_orientation_depends_size(image)
        size = config.A4_LANDSCAPE if orientation == entity.Orientation.LANDSCAPE.value else config.A4_PORTRAIT
        image.thumbnail(size, Image.Resampling.LANCZOS)
        new_img = Image.new("RGB", size, "white")
        x_offset = (size[0] - image.width) // 2
        y_offset = (size[1] - image.height) // 2
        new_img.paste(image, (x_offset, y_offset))
        return new_img

    def get_orientation_depends_size(self, image: Image) -> str:
        if image.width > image.height:
            return entity.Orientation.LANDSCAPE.value
        else:
            return entity.Orientation.PORTRAIT.value

    def from_word_to_pdf(self, files: list[bytes]) -> io.BytesIO:
        """Конвертирует Word (docx) в PDF используя LibreOffice (без сохранения на диск)"""

        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_docx:
            temp_docx.write(files[0])
            temp_docx.flush()
            temp_docx_path = Path(temp_docx.name)

        output_pdf_path = temp_docx_path.with_suffix(".pdf")

        # Запускаем LibreOffice для конвертации
        subprocess.run([
            "libreoffice", "--headless", "--convert-to", "pdf",
            str(temp_docx_path), "--outdir", str(temp_docx_path.parent)
        ], check=True)

        # Читаем PDF в память
        with open(output_pdf_path, "rb") as pdf_file:
            pdf_bytes = pdf_file.read()

        # Удаляем временные файлы
        temp_docx_path.unlink(missing_ok=True)
        output_pdf_path.unlink(missing_ok=True)

        return io.BytesIO(pdf_bytes)

    def from_powerpoint_to_pdf(self, files: list[bytes]) -> io.BytesIO:
        """Конвертирует Word (docx) в PDF используя LibreOffice (без сохранения на диск)"""

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pptx") as temp_docx:
            temp_docx.write(files[0])
            temp_docx.flush()
            temp_docx_path = Path(temp_docx.name)

        output_pdf_path = temp_docx_path.with_suffix(".pdf")

        # Запускаем LibreOffice для конвертации
        subprocess.run([
            "libreoffice", "--headless", "--convert-to", "pdf",
            str(temp_docx_path), "--outdir", str(temp_docx_path.parent)
        ], check=True)

        # Читаем PDF в память
        with open(output_pdf_path, "rb") as pdf_file:
            pdf_bytes = pdf_file.read()

        # Удаляем временные файлы
        temp_docx_path.unlink(missing_ok=True)
        output_pdf_path.unlink(missing_ok=True)

        return io.BytesIO(pdf_bytes)

    def from_excel_to_pdf(self, files: list[bytes]) -> io.BytesIO:
        """Конвертирует Excel (bytes) в PDF (bytes)"""
        excel_stream = io.BytesIO(files[0])
        df = pd.read_excel(excel_stream)
        html_content = df.to_html(index=False, border=1)

        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf_file:
            temp_pdf_path = temp_pdf_file.name

        options = {
            "page-size": "A4",
            "encoding": "UTF-8",
            "no-outline": None
        }

        pdfkit.from_string(html_content, temp_pdf_path, options=options)
        with open(temp_pdf_path, 'rb') as f:
            pdf_stream = io.BytesIO(f.read())

        os.remove(temp_pdf_path)

        pdf_stream.seek(0)
        return pdf_stream

    def from_html_to_pdf(self, files: list[bytes]) -> io.BytesIO:
        """Конвертирует Html (bytes) в PDF (bytes)"""
        html_content = files[0].decode('utf-8')

        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf_file:
            temp_pdf_path = temp_pdf_file.name

        options = {
            "page-size": "A4",
            "encoding": "UTF-8",
            "no-outline": None
        }

        pdfkit.from_string(html_content, temp_pdf_path, options=options)
        with open(temp_pdf_path, 'rb') as f:
            pdf_stream = io.BytesIO(f.read())

        os.remove(temp_pdf_path)

        pdf_stream.seek(0)
        return pdf_stream
