import io
import os
import subprocess
import tempfile
from pathlib import Path

import pandas as pd
import pdfkit
from PIL import Image
from docx import Document
from docx.shared import Inches

from app import entity
from app.config import config
from app.logger import logger
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
        return self._convert_by_libreoffice(files, ".docs")

    def from_powerpoint_to_pdf(self, files: list[bytes]) -> io.BytesIO:
        return self._convert_by_libreoffice(files, ".pptx")

    def from_txt_to_pdf(self, files: list[bytes]) -> io.BytesIO:
        return self._convert_by_libreoffice(files, ".txt")

    def _convert_by_libreoffice(self, files: list[bytes], suffix: str) -> io.BytesIO:
        """Конвертирует документ в PDF используя LibreOffice (без сохранения на диск)"""

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            logger.info(f"{temp_file.name=}")
            temp_file.write(files[0])
            temp_file.flush()
            temp_path = Path(temp_file.name)

        output_pdf_path = temp_path.with_suffix(".pdf")

        # Запускаем LibreOffice для конвертации
        subprocess.run([
            "libreoffice", "--headless", "--convert-to", "pdf",
            str(temp_path), "--outdir", str(temp_path.parent)
        ], check=True)

        # Читаем PDF в память
        with open(output_pdf_path, "rb") as pdf_file:
            pdf_bytes = pdf_file.read()

        # Удаляем временные файлы
        temp_path.unlink(missing_ok=True)
        output_pdf_path.unlink(missing_ok=True)

        return io.BytesIO(pdf_bytes)

    def from_excel_to_pdf(self, files: list[bytes]) -> io.BytesIO:
        """Конвертирует Excel (bytes) в PDF (bytes)"""
        file_stream = io.BytesIO(files[0])
        df = pd.read_excel(file_stream)
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

    def from_csv_to_pdf(self, files: list[bytes]) -> io.BytesIO:
        """Конвертирует Excel (bytes) в PDF (bytes)"""
        file_stream = io.BytesIO(files[0])
        df = pd.read_csv(file_stream)
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

    def from_jpg_to_word(self, files: list[bytes]) -> io.BytesIO:
        doc = Document()
        # doc.add_heading("Images to Word", level=1)  # Заголовок

        # Добавляем изображения в документ
        for idx, img_bytes in enumerate(files):
            # Читаем изображение из байтов
            img_stream = io.BytesIO(img_bytes)
            # doc.add_paragraph(f"Image {idx + 1}")  # Подпись к изображению
            doc.add_picture(img_stream, width=Inches(5))  # Добавляем изображение (ширина 5 дюймов)
            doc.add_paragraph("\n")  # Отступ

        # Сохраняем документ в памяти с помощью BytesIO
        doc_stream = io.BytesIO()
        doc.save(doc_stream)
        doc_stream.seek(0)  # Сброс позиции потока, чтобы его можно было прочитать

        return doc_stream

    def from_csv_to_excel(self, files: list[bytes]) -> io.BytesIO:
        """Конвертирует Excel (bytes) в PDF (bytes)"""
        file_stream = io.BytesIO(files[0])
        df = pd.read_csv(file_stream)

        output_buffer = io.BytesIO()
        df.to_excel(output_buffer, index=False)
        output_buffer.seek(0)
        return output_buffer

    def from_excel_to_csv(self, files: list[bytes]) -> io.BytesIO:
        """Конвертирует Excel (bytes) в PDF (bytes)"""
        file_stream = io.BytesIO(files[0])
        df = pd.read_excel(file_stream)

        output_buffer = io.BytesIO()
        df.to_csv(output_buffer, index=False, encoding="utf-8")
        output_buffer.seek(0)
        return output_buffer
