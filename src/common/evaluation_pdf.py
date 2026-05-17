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


def _prepare_image(image_bytes: bytes) -> Tuple[bytes, int, int]:
    """
    Convert image to RGB JPEG bytes for proper PDF embedding.
    """
    image = Image.open(BytesIO(image_bytes))

    if image.mode != "RGB":
        image = image.convert("RGB")

    width, height = image.size

    output = BytesIO()

    image.save(
        output,
        format="JPEG",
        quality=75,
        optimize=True,
    )

    output.seek(0)

    return output.read(), width, height


class _PdfCanvas:
    def __init__(self) -> None:
        self.pages: list[list[str]] = []
        self.commands: list[str] = []

        self.images: list[dict] = []

        self.y = PAGE_HEIGHT - MARGIN

        self._new_page()

    def _new_page(self) -> None:
        if self.commands:
            self.pages.append(self.commands)

        self.commands = [
            "0 0 0 rg",
            "0 0 0 RG",
            "0.5 w",
        ]

        self.y = PAGE_HEIGHT - MARGIN

    def ensure_space(self, height: int) -> None:
        if self.y - height < BOTTOM_MARGIN:
            self._new_page()

    def text(
        self,
        x: int,
        y: int,
        value: Any,
        size: int = 10,
        bold: bool = False,
    ) -> None:
        font = "F2" if bold else "F1"

        self.commands.append(
            f"BT /{font} {size} Tf {x} {y} Td " f"({_escape_pdf_text(value)}) Tj ET"
        )

    def line(self, y: int) -> None:
        self.commands.append(f"{MARGIN} {y} m {PAGE_WIDTH - MARGIN} {y} l S")

    def section(self, title: str) -> None:
        self.ensure_space(34)

        self.text(MARGIN, self.y, title.upper(), 12, bold=True)

        self.y -= 7

        self.line(self.y)

        self.y -= 18

    def key_value(
        self,
        x: int,
        key: str,
        value: Any,
    ) -> None:
        self.text(x, self.y, f"{key}:", 9, bold=True)

        self.text(
            x + 110,
            self.y,
            _format_value(value),
            9,
        )

    def pairs(
        self,
        title: str,
        items: list[tuple[str, Any]],
    ) -> None:
        self.section(title)

        for index in range(0, len(items), 2):
            self.ensure_space(LINE_HEIGHT)

            left = items[index]

            right = items[index + 1] if index + 1 < len(items) else None

            self.key_value(
                MARGIN,
                left[0],
                left[1],
            )

            if right:
                self.key_value(
                    310,
                    right[0],
                    right[1],
                )

            self.y -= LINE_HEIGHT

        self.y -= 6

    def paragraph(
        self,
        title: str,
        value: Any,
    ) -> None:
        self.section(title)

        text = _format_value(value)

        for line in wrap(text, width=92) or ["-"]:
            self.ensure_space(LINE_HEIGHT)

            self.text(
                MARGIN,
                self.y,
                line,
                9,
            )

            self.y -= LINE_HEIGHT

        self.y -= 6

    def table_header(
        self,
        headers: list[str],
    ) -> None:
        self.ensure_space(20)

        x_positions = [
            MARGIN,
            170,
            310,
            450,
        ]

        for i, header in enumerate(headers):
            self.text(
                x_positions[i],
                self.y,
                header,
                10,
                bold=True,
            )

        self.y -= 15

        self.line(self.y)

        self.y -= 10

    def table_row(
        self,
        values: list[Any],
    ) -> None:
        self.ensure_space(18)

        x_positions = [
            MARGIN,
            170,
            310,
            450,
        ]

        for i, value in enumerate(values):
            self.text(
                x_positions[i],
                self.y,
                _format_value(value),
                9,
            )

        self.y -= 14

    def add_image(
        self,
        image_bytes: bytes,
    ) -> int:
        jpeg_bytes, width, height = _prepare_image(image_bytes)

        image_index = len(self.images) + 1

        self.images.append(
            {
                "index": image_index,
                "bytes": jpeg_bytes,
                "width": width,
                "height": height,
            }
        )

        return image_index

    def image_block(
        self,
        image_index: int,
        title: str,
        photo_name: str | None = None,
        position: int = 0,
    ) -> None:
        image_width = 240
        image_height = 150

        gap = 30

        # LEFT / RIGHT POSITION
        x = MARGIN if position % 2 == 0 else MARGIN + image_width + gap

        # NEW ROW ONLY FOR LEFT IMAGE
        if position % 2 == 0:
            self.ensure_space(220)

        label = photo_name or title

        self.text(
            x,
            self.y,
            label,
            10,
            bold=True,
        )

        image_y = self.y - 20 - image_height

        # DRAW IMAGE
        self.commands.append(
            f"q\n"
            f"{image_width} 0 0 {image_height} {x} {image_y} cm\n"
            f"/Im{image_index} Do\n"
            f"Q"
        )

        # MOVE TO NEXT ROW AFTER RIGHT IMAGE
        if position % 2 == 1:
            self.y -= image_height + 50

    def finish(self) -> None:
        if self.commands:
            self.pages.append(self.commands)

            self.commands = []


def _build_pdf(
    page_commands: list[list[str]],
    images: list[dict],
) -> bytes:
    objects: list[bytes | None] = [None] * 10000

    page_refs = []

    objects[1] = b"<< /Type /Catalog /Pages 2 0 R >>"

    objects[3] = b"<< /Type /Font /Subtype /Type1 " b"/BaseFont /Helvetica >>"

    objects[4] = b"<< /Type /Font /Subtype /Type1 " b"/BaseFont /Helvetica-Bold >>"

    obj_index = 5

    image_object_map = {}

    # IMAGE OBJECTS
    for image in images:
        image_obj = obj_index

        obj_index += 1

        image_object_map[image["index"]] = image_obj

        image_stream = (
            (
                f"<< /Type /XObject "
                f"/Subtype /Image "
                f"/Width {image['width']} "
                f"/Height {image['height']} "
                f"/ColorSpace /DeviceRGB "
                f"/BitsPerComponent 8 "
                f"/Filter /DCTDecode "
                f"/Length {len(image['bytes'])} >>\n"
                f"stream\n"
            ).encode("latin-1")
            + image["bytes"]
            + b"\nendstream"
        )

        objects[image_obj] = image_stream

    # PAGE OBJECTS
    for commands in page_commands:
        page_obj = obj_index
        content_obj = obj_index + 1

        obj_index += 2

        page_refs.append(f"{page_obj} 0 R")

        content_stream = "\n".join(commands).encode("latin-1")

        resources = "<< /Font << " "/F1 3 0 R " "/F2 4 0 R " ">> " "/XObject << "

        for image in images:
            image_obj = image_object_map[image["index"]]

            resources += f"/Im{image['index']} " f"{image_obj} 0 R "

        resources += ">> >>"

        objects[page_obj] = (
            f"<< /Type /Page "
            f"/Parent 2 0 R "
            f"/MediaBox [0 0 {PAGE_WIDTH} {PAGE_HEIGHT}] "
            f"/Resources {resources} "
            f"/Contents {content_obj} 0 R >>"
        ).encode("latin-1")

        objects[content_obj] = (
            (f"<< /Length {len(content_stream)} >>\n" f"stream\n").encode("latin-1")
            + content_stream
            + b"\nendstream"
        )

    objects[2] = (
        f"<< /Type /Pages "
        f"/Kids [{' '.join(page_refs)}] "
        f"/Count {len(page_refs)} >>"
    ).encode("latin-1")

    pdf = bytearray(b"%PDF-1.4\n")

    offsets = [0]

    for object_number in range(1, obj_index):
        offsets.append(len(pdf))

        pdf.extend(f"{object_number} 0 obj\n".encode("latin-1"))

        pdf.extend(objects[object_number] or b"")

        pdf.extend(b"\nendobj\n")

    xref_offset = len(pdf)

    pdf.extend(f"xref\n0 {obj_index}\n".encode("latin-1"))

    pdf.extend(b"0000000000 65535 f \n")

    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("latin-1"))

    pdf.extend(
        (
            f"trailer\n"
            f"<< /Size {obj_index} /Root 1 0 R >>\n"
            f"startxref\n"
            f"{xref_offset}\n"
            f"%%EOF\n"
        ).encode("latin-1")
    )

    return bytes(pdf)


def build_buy_lead_evaluation_pdf(
    evaluation: Mapping[str, Any],
) -> bytes:
    canvas = _PdfCanvas()

    canvas.text(
        MARGIN,
        canvas.y,
        "POC CARS",
        18,
        bold=True,
    )

    canvas.text(
        390,
        canvas.y,
        f"Evaluation ID: {evaluation.get('evaluation_id')}",
        10,
    )

    canvas.y -= 20

    canvas.text(
        MARGIN,
        canvas.y,
        "Evaluation Report",
        14,
        bold=True,
    )

    canvas.text(
        390,
        canvas.y,
        ("Generated: " f"{datetime.now().strftime('%d-%m-%Y %H:%M')}"),
        9,
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
            ("Payment Name", evaluation.get("payment_name")),
            ("Alternate Mobile", evaluation.get("alternate_mobile")),
            ("Source", evaluation.get("source")),
            ("Mode", evaluation.get("mode")),
            ("Broker", evaluation.get("broker_name")),
            ("Status", evaluation.get("status")),
            ("Telecaller", evaluation.get("telecaller")),
            ("Executive", evaluation.get("executive")),
            ("Vehicle", vehicle_name),
            ("Fuel", evaluation.get("fuel_type")),
            ("MFG Year", evaluation.get("mfg_year")),
            ("KMS", evaluation.get("kms")),
            ("Owner", evaluation.get("owner")),
            ("Color", evaluation.get("color")),
        ],
    )

    canvas.pairs(
        "Vehicle Details",
        [
            ("Registration No", evaluation.get("registration_no")),
            ("Transmission", evaluation.get("transmission")),
            ("Cubic Capacity", evaluation.get("cubic_capacity")),
            ("Push Button", evaluation.get("push_button")),
            ("Company Invoice", evaluation.get("company_invoice")),
            ("NOC", evaluation.get("noc")),
            ("Reg Month", evaluation.get("reg_month")),
            ("Reg Year", evaluation.get("reg_year")),
            ("Euro", evaluation.get("euro")),
            ("RC Book", evaluation.get("rc_book")),
            ("Second Key", evaluation.get("second_key")),
            ("Hypo", evaluation.get("hypo")),
            ("Hypo Bank", evaluation.get("hypo_bank")),
            ("Service Record", evaluation.get("service_record")),
            ("PUC", evaluation.get("puc")),
            ("Memo", evaluation.get("memo")),
            ("Memo Amount", _format_money(evaluation.get("memo_amount"))),
            ("Memo Paid", evaluation.get("memo_paid")),
            ("MV Tax", _format_money(evaluation.get("mv_tax"))),
            ("RMA", evaluation.get("rma")),
            ("Taxi/Private", evaluation.get("taxi_private")),
            ("Other NOC", evaluation.get("other_noc")),
            ("Blacklist", evaluation.get("blacklist")),
            ("RTO Status", evaluation.get("rto_status")),
        ],
    )

    canvas.pairs(
        "Insurance Details",
        [
            ("Online Insurance", evaluation.get("online_insurance")),
            ("Insurance Type", evaluation.get("insurance_type")),
            ("CP/ZD Company", evaluation.get("cp_zd_company")),
            ("TP Company", evaluation.get("tp_company")),
            ("CP/ZD Date", evaluation.get("cp_zd_date")),
            ("TP Date", evaluation.get("tp_date")),
            ("IDV", _format_money(evaluation.get("idv"))),
            ("NCB", _format_money(evaluation.get("ncb"))),
            ("Premium", _format_money(evaluation.get("premium"))),
        ],
    )

    canvas.section("Evaluation Details")

    canvas.table_header(
        [
            "Part",
            "Sub Part",
            "Status",
            "Sub Status",
        ]
    )

    for item in evaluation.get(
        "evaluation_parameters",
        [],
    ):
        canvas.table_row(
            [
                item.get("part_name"),
                item.get("subpart_name"),
                item.get("subpart_status"),
                item.get("subpart_sub_status"),
            ]
        )

    canvas.y -= 10
    canvas.section("Vehicle Photos")

    for idx, photo in enumerate(
        evaluation.get("photos", []),
    ):
        image_index = canvas.add_image(photo["image_bytes"])

        canvas.image_block(
            image_index=image_index,
            title=f"Photo {idx + 1}",
            photo_name=photo.get("photo_name"),
            position=idx,
        )

    # HANDLE ODD IMAGE COUNT
    if len(evaluation.get("photos", [])) % 2 != 0:
        canvas.y -= 230

    canvas.paragraph(
        "Lead Remarks",
        evaluation.get("lead_remarks"),
    )

    canvas.paragraph(
        "Evaluation Remarks",
        evaluation.get("evaluation_remarks"),
    )

    canvas.finish()

    return _build_pdf(
        canvas.pages,
        canvas.images,
    )
