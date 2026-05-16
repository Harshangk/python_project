from datetime import date, datetime
from decimal import Decimal
from io import BytesIO
from textwrap import wrap
from typing import Any, Mapping, Tuple

from PIL import Image

from app.constant import BOTTOM_MARGIN, LINE_HEIGHT, MARGIN, PAGE_HEIGHT, PAGE_WIDTH


def _escape_pdf_text(value: Any) -> str:
    text = "" if value is None else str(value)
    text = text.encode("latin-1", "replace").decode("latin-1")
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _format_value(value: Any) -> str:
    if value is None or value == "":
        return "-"
    if isinstance(value, datetime):
        return value.strftime("%d-%m-%Y %H:%M")
    if isinstance(value, date):
        return value.strftime("%d-%m-%Y")
    if isinstance(value, Decimal):
        return f"{value:,.2f}"
    return str(value)


def _format_money(value: Any) -> str:
    if value is None:
        value = Decimal("0.00")
    if not isinstance(value, Decimal):
        value = Decimal(str(value))
    return f"INR {value:,.2f}"


def _get_image_info(image_bytes: bytes) -> Tuple[int, int, str]:
    img = Image.open(BytesIO(image_bytes))
    width, height = img.size
    format_type = img.format.lower()
    return width, height, format_type


class _PdfCanvas:
    def __init__(self) -> None:
        self.pages: list[list[str]] = []
        self.commands: list[str] = []

        # NEW: store images for PDF embedding
        self.images: list[dict] = []

        self.y = PAGE_HEIGHT - MARGIN
        self._new_page()

    def _new_page(self) -> None:
        if self.commands:
            self.pages.append(self.commands)
        self.commands = ["0 0 0 rg", "0 0 0 RG", "0.5 w"]
        self.y = PAGE_HEIGHT - MARGIN

    def ensure_space(self, height: int) -> None:
        if self.y - height < BOTTOM_MARGIN:
            self._new_page()

    def text(
        self, x: int, y: int, value: Any, size: int = 10, bold: bool = False
    ) -> None:
        font = "F2" if bold else "F1"
        self.commands.append(
            f"BT /{font} {size} Tf {x} {y} Td ({_escape_pdf_text(value)}) Tj ET"
        )

    def line(self, y: int) -> None:
        self.commands.append(f"{MARGIN} {y} m {PAGE_WIDTH - MARGIN} {y} l S")

    def section(self, title: str) -> None:
        self.ensure_space(34)
        self.text(MARGIN, self.y, title.upper(), 12, bold=True)
        self.y -= 7
        self.line(self.y)
        self.y -= 18

    def key_value(self, x: int, key: str, value: Any) -> None:
        self.text(x, self.y, f"{key}:", 9, bold=True)
        self.text(x + 110, self.y, _format_value(value), 9)

    def pairs(self, title: str, items: list[tuple[str, Any]]) -> None:
        self.section(title)
        for index in range(0, len(items), 2):
            self.ensure_space(LINE_HEIGHT)
            left = items[index]
            right = items[index + 1] if index + 1 < len(items) else None

            self.key_value(MARGIN, left[0], left[1])
            if right:
                self.key_value(310, right[0], right[1])

            self.y -= LINE_HEIGHT
        self.y -= 6

    def paragraph(self, title: str, value: Any) -> None:
        self.section(title)
        text = _format_value(value)
        for line in wrap(text, width=92) or ["-"]:
            self.ensure_space(LINE_HEIGHT)
            self.text(MARGIN, self.y, line, 9)
            self.y -= LINE_HEIGHT
        self.y -= 6

    def table_header(self, headers: list[str]) -> None:
        self.ensure_space(20)
        x_positions = [MARGIN, 170, 310, 450]

        for i, header in enumerate(headers):
            self.text(x_positions[i], self.y, header, 10, bold=True)

        self.y -= 15
        self.line(self.y)
        self.y -= 10

    def table_row(self, values: list[Any]) -> None:
        self.ensure_space(18)
        x_positions = [MARGIN, 170, 310, 450]

        for i, value in enumerate(values):
            self.text(x_positions[i], self.y, _format_value(value), 9)

        self.y -= 14

    # TEXT PLACEHOLDER (kept for layout spacing only)
    def image_block(self, title: str, photo_type: str = None) -> None:
        self.ensure_space(120)
        label = f"{title}" + (f" ({photo_type})" if photo_type else "")
        self.text(MARGIN, self.y, "[PHOTO]", 10, bold=True)
        self.y -= 12
        self.text(MARGIN, self.y, label, 9)
        self.y -= 10

        # reserve space for image
        self.y -= 80

    # NEW: register real image
    def add_image(self, image_bytes: bytes, label: str) -> None:
        width, height, fmt = _get_image_info(image_bytes)

        self.images.append(
            {
                "bytes": image_bytes,
                "width": width,
                "height": height,
                "label": label,
                "format": fmt,
            }
        )

    def finish(self) -> None:
        if self.commands:
            self.pages.append(self.commands)
            self.commands = []


def _build_pdf(page_commands: list[list[str]], images: list[dict]) -> bytes:
    objects: list[bytes | None] = [None] * 10000
    page_refs = []
    image_refs = []

    objects[1] = b"<< /Type /Catalog /Pages 2 0 R >>"
    objects[3] = b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"
    objects[4] = b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>"

    obj_index = 5

    for img in images:
        img_bytes = img["bytes"]
        w, h = img["width"], img["height"]

        img_obj = obj_index
        obj_index += 1

        stream = (
            (
                f"<< /Type /XObject /Subtype /Image /Width {w} /Height {h} "
                f"/ColorSpace /DeviceRGB /BitsPerComponent 8 "
                f"/Filter /DCTDecode /Length {len(img_bytes)} >>\nstream\n"
            ).encode("latin-1")
            + img_bytes
            + b"\nendstream"
        )

        objects[img_obj] = stream
        image_refs.append(f"{img_obj} 0 R")

    # PAGES
    for index, commands in enumerate(page_commands):
        page_obj = obj_index
        content_obj = obj_index + 1
        obj_index += 2

        page_refs.append(f"{page_obj} 0 R")

        stream = "\n".join(commands).encode("latin-1")

        resources = "<< /Font << /F1 3 0 R /F2 4 0 R >> " "/XObject << "

        for i, ref in enumerate(image_refs):
            resources += f"/Im{i+1} {ref} "

        resources += ">> >>"

        objects[page_obj] = (
            f"<< /Type /Page /Parent 2 0 R "
            f"/MediaBox [0 0 {PAGE_WIDTH} {PAGE_HEIGHT}] "
            f"/Resources {resources} "
            f"/Contents {content_obj} 0 R >>"
        ).encode("latin-1")

        objects[content_obj] = (
            f"<< /Length {len(stream)} >>\nstream\n".encode("latin-1")
            + stream
            + b"\nendstream"
        )

    objects[2] = (
        f"<< /Type /Pages /Kids [{' '.join(page_refs)}] /Count {len(page_refs)} >>"
    ).encode("latin-1")

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]

    for i in range(1, obj_index):
        offsets.append(len(pdf))
        pdf.extend(f"{i} 0 obj\n".encode("latin-1"))
        pdf.extend(objects[i] or b"")
        pdf.extend(b"\nendobj\n")

    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {obj_index}\n".encode("latin-1"))
    pdf.extend(b"0000000000 65535 f \n")

    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("latin-1"))

    pdf.extend(
        f"trailer\n<< /Size {obj_index} /Root 1 0 R >>\n \
            startxref\n{xref_offset}\n%%EOF\n".encode(
            "latin-1"
        )
    )

    return bytes(pdf)


def build_buy_lead_evaluation_pdf(evaluation: Mapping[str, Any]) -> bytes:
    canvas = _PdfCanvas()

    canvas.text(MARGIN, canvas.y, "POC CARS", 18, bold=True)
    canvas.text(390, canvas.y, f"Evaluation ID: {evaluation.get('evaluation_id')}", 10)
    canvas.y -= 20

    canvas.text(MARGIN, canvas.y, "Evaluation Report", 14, bold=True)
    canvas.text(
        390, canvas.y, f"Generated: {datetime.now().strftime('%d-%m-%Y %H:%M')}", 9
    )

    canvas.y -= 12
    canvas.line(canvas.y)
    canvas.y -= 22

    vehicle_name = " ".join(
        _format_value(evaluation.get(key))
        for key in ("make", "model", "variant")
        if evaluation.get(key)
    )

    canvas.pairs(
        "Lead Details",
        [
            ("Lead ID", evaluation.get("lead_id")),
            ("Branch", evaluation.get("branch")),
            ("Customer", evaluation.get("customer_name")),
            ("Mobile", evaluation.get("mobile")),
            ("Evaluation Name", evaluation.get("evaluation_name")),
            ("Vehicle", vehicle_name),
        ],
    )

    canvas.pairs(
        "Vehicle Details",
        [
            ("Registration No", evaluation.get("registration_no")),
            ("Transmission", evaluation.get("transmission")),
            ("Fuel", evaluation.get("fuel_type")),
        ],
    )

    canvas.pairs(
        "Insurance Details",
        [
            ("Insurance Type", evaluation.get("insurance_type")),
            ("IDV", _format_money(evaluation.get("idv"))),
        ],
    )

    canvas.section("Evaluation Details")

    canvas.table_header(["Part", "Sub Part", "Status", "Sub Status"])

    for item in evaluation.get("evaluation_parameters", []):
        canvas.table_row(
            [
                item.get("part_name"),
                item.get("subpart_name"),
                item.get("subpart_status"),
                item.get("subpart_sub_status"),
            ]
        )

    # PHOTOS
    canvas.section("Vehicle Photos")

    for idx, photo in enumerate(evaluation.get("photos", []), start=1):
        label = f"Photo {idx}"
        canvas.image_block(label, photo.get("photo_type"))

        # REAL IMAGE EMBED
        canvas.add_image(photo["image_bytes"], label)

    canvas.paragraph("Lead Remarks", evaluation.get("lead_remarks"))
    canvas.paragraph("Evaluation Remarks", evaluation.get("evaluation_remarks"))

    canvas.finish()

    return _build_pdf(canvas.pages, canvas.images)
