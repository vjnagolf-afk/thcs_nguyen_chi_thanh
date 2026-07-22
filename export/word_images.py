# -*- coding: utf-8 -*-

import io
import base64
import logging
import urllib.request

from typing import Dict, Any, Optional

import docx

from docx.shared import (
    Inches,
    Pt,
    RGBColor
)

from docx.enum.text import (
    WD_PARAGRAPH_ALIGNMENT
)


logger = logging.getLogger(
    "WordImageEngine"
)


class ImageRenderer:

    MAX_A4_WIDTH_INCHES = 6.0

    @classmethod
    def _fetch_image(
        cls,
        source: str
    ) -> Optional[io.BytesIO]:

        try:

            if not source:
                return None

            if source.startswith(
                (
                    "http://",
                    "https://"
                )
            ):

                request = urllib.request.Request(
                    source,
                    headers={
                        "User-Agent":
                        "Mozilla/5.0"
                    }
                )

                with urllib.request.urlopen(
                    request,
                    timeout=15
                ) as response:

                    return io.BytesIO(
                        response.read()
                    )

            with open(
                source,
                "rb"
            ) as file:

                return io.BytesIO(
                    file.read()
                )

        except Exception as error:

            logger.error(
                "Không thể tải ảnh %s: %s",
                source,
                error
            )

            return None

    @classmethod
    def _insert_picture_safe(
        cls,
        doc: docx.Document,
        image_stream: io.BytesIO,
        width_inches: Optional[float] = None
    ):

        paragraph = doc.add_paragraph()

        paragraph.alignment = (
            WD_PARAGRAPH_ALIGNMENT.CENTER
        )

        run = paragraph.add_run()

        try:

            safe_width = min(
                width_inches
                if width_inches
                else cls.MAX_A4_WIDTH_INCHES,
                cls.MAX_A4_WIDTH_INCHES
            )

            image_stream.seek(0)

            run.add_picture(
                image_stream,
                width=Inches(
                    safe_width
                )
            )

        except Exception as error:

            logger.error(
                "Lỗi chèn ảnh: %s",
                error
            )

            run.add_text(
                "[Không thể hiển thị hình ảnh]"
            )

        paragraph.paragraph_format.space_after = Pt(6)

    @classmethod
    def render_image(
        cls,
        doc: docx.Document,
        node: Dict[str, Any]
    ):

        url = (
            node.get("url", "")
            .strip()
        )

        alt = node.get(
            "alt",
            "Hình ảnh"
        )

        if not url:
            return

        image_stream = cls._fetch_image(
            url
        )

        if image_stream:

            cls._insert_picture_safe(
                doc,
                image_stream
            )

        else:

            paragraph = doc.add_paragraph()

            paragraph.alignment = (
                WD_PARAGRAPH_ALIGNMENT.CENTER
            )

            run = paragraph.add_run(
                f"[Hình ảnh: {alt}]"
            )

            run.font.italic = True

            run.font.color.rgb = RGBColor(
                128,
                128,
                128
            )

    @classmethod
    def add_logo(
        cls,
        doc: docx.Document,
        logo_path: str,
        width_inches: float = 1.0
    ):

        image_stream = cls._fetch_image(
            logo_path
        )

        if image_stream:

            cls._insert_picture_safe(
                doc,
                image_stream,
                width_inches
            )

    @classmethod
    def render_mermaid(
        cls,
        doc: docx.Document,
        mermaid_code: str
    ):

        try:

            encoded = base64.urlsafe_b64encode(
                mermaid_code.encode(
                    "utf-8"
                )
            ).decode(
                "utf-8"
            )

            image_url = (
                "https://mermaid.ink/img/"
                f"{encoded}?type=png"
            )

            image_stream = cls._fetch_image(
                image_url
            )

            if not image_stream:

                raise RuntimeError(
                    "Không tải được sơ đồ Mermaid"
                )

            cls._insert_picture_safe(
                doc,
                image_stream,
                5.0
            )

        except Exception as error:

            logger.error(
                "Lỗi Mermaid: %s",
                error
            )

            paragraph = doc.add_paragraph(
                "[Sơ đồ Mermaid không thể hiển thị]"
            )

            paragraph.alignment = (
                WD_PARAGRAPH_ALIGNMENT.CENTER
            )

    @classmethod
    def add_qr_code(
        cls,
        doc: docx.Document,
        data: str,
        width_inches: float = 1.5
    ):

        try:

            import qrcode

            qr = qrcode.QRCode(
                version=1,
                error_correction=(
                    qrcode.constants
                    .ERROR_CORRECT_M
                ),
                box_size=10,
                border=4
            )

            qr.add_data(data)
            qr.make(fit=True)

            image = qr.make_image(
                fill_color="black",
                back_color="white"
            )

            buffer = io.BytesIO()

            image.save(
                buffer,
                format="PNG"
            )

            buffer.seek(0)

            cls._insert_picture_safe(
                doc,
                buffer,
                width_inches
            )

        except ImportError:

            logger.error(
                "Thiếu thư viện qrcode. "
                "Cài đặt: pip install qrcode"
            )

        except Exception as error:

            logger.error(
                "Lỗi tạo QR: %s",
                error
            )
