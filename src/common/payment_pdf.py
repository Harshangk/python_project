from datetime import date, datetime
from decimal import Decimal
from textwrap import wrap
from typing import Any, Mapping

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


class _PdfCanvas:
    def __init__(self) -> None:
        self.pages: list[list[str]] = []
        self.commands: list[str] = []
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
        self,
        x: int,
        y: int,
        value: Any,
        size: int = 10,
        bold: bool = False,
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

    def finish(self) -> None:
        if self.commands:
            self.pages.append(self.commands)
            self.commands = []


def _build_pdf(page_commands: list[list[str]]) -> bytes:
    object_count = 4 + (len(page_commands) * 2)
    objects: list[bytes | None] = [None] * (object_count + 1)
    page_refs = []

    objects[1] = b"<< /Type /Catalog /Pages 2 0 R >>"
    objects[3] = b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"
    objects[4] = b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>"

    for index, commands in enumerate(page_commands):
        page_obj = 5 + (index * 2)
        content_obj = page_obj + 1
        page_refs.append(f"{page_obj} 0 R")
        stream = "\n".join(commands).encode("latin-1")
        objects[page_obj] = (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {PAGE_WIDTH} "
            f"{PAGE_HEIGHT}] /Resources << /Font << /F1 3 0 R /F2 4 0 R >> >> "
            f"/Contents {content_obj} 0 R >>"
        ).encode("latin-1")
        objects[content_obj] = (
            f"<< /Length {len(stream)} >>\nstream\n".encode("latin-1")
            + stream
            + b"\nendstream"
        )

    objects[2] = (
        f"<< /Type /Pages /Kids [{' '.join(page_refs)}] " f"/Count {len(page_refs)} >>"
    ).encode("latin-1")

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for object_number in range(1, object_count + 1):
        body = objects[object_number]
        if body is None:
            body = b""
        offsets.append(len(pdf))
        pdf.extend(f"{object_number} 0 obj\n".encode("latin-1"))
        pdf.extend(body)
        pdf.extend(b"\nendobj\n")

    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {object_count + 1}\n".encode("latin-1"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("latin-1"))
    pdf.extend(
        (
            f"trailer\n<< /Size {object_count + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF\n"
        ).encode("latin-1")
    )
    return bytes(pdf)


def build_buy_lead_payment_pdf(payment: Mapping[str, Any]) -> bytes:
    canvas = _PdfCanvas()
    canvas.text(MARGIN, canvas.y, "POC CARS", 18, bold=True)
    canvas.text(390, canvas.y, f"Payment ID: {payment.get('payment_id')}", 10)
    canvas.y -= 20
    canvas.text(MARGIN, canvas.y, "Payment Requisition Form", 14, bold=True)
    canvas.text(
        390,
        canvas.y,
        f"Generated: {datetime.now().strftime('%d-%m-%Y %H:%M')}",
        9,
    )
    canvas.y -= 12
    canvas.line(canvas.y)
    canvas.y -= 22

    vehicle_name = " ".join(
        _format_value(payment.get(key))
        for key in ("make", "model", "variant")
        if payment.get(key)
    )

    canvas.pairs(
        "Lead Details",
        [
            ("Lead ID", payment.get("lead_id")),
            ("Branch", payment.get("branch")),
            ("Customer", payment.get("customer_name")),
            ("Mobile", payment.get("mobile")),
            ("Payment Name", payment.get("payment_name")),
            ("Alternate Mobile", payment.get("alternate_mobile")),
            ("Source", payment.get("source")),
            ("Mode", payment.get("mode")),
            ("Broker", payment.get("broker_name")),
            ("Status", payment.get("status")),
            ("Telecaller", payment.get("telecaller")),
            ("Executive", payment.get("executive")),
            ("Vehicle", vehicle_name),
            ("Fuel", payment.get("fuel_type")),
            ("MFG Year", payment.get("mfg_year")),
            ("KMS", payment.get("kms")),
            ("Owner", payment.get("owner")),
            ("Color", payment.get("color")),
        ],
    )

    canvas.pairs(
        "Vehicle Details",
        [
            ("Registration No", payment.get("registration_no")),
            ("Transmission", payment.get("transmission")),
            ("Cubic Capacity", payment.get("cubic_capacity")),
            ("Chassis No", payment.get("chassis_no")),
            ("Engine No", payment.get("engine_no")),
            ("Push Button", payment.get("push_button")),
            ("Company Invoice", payment.get("company_invoice")),
            ("NOC", payment.get("noc")),
            ("Reg Month", payment.get("reg_month")),
            ("Reg Year", payment.get("reg_year")),
            ("Euro", payment.get("euro")),
            ("RC Book", payment.get("rc_book")),
            ("Second Key", payment.get("second_key")),
            ("Hypo", payment.get("hypo")),
            ("Hypo Bank", payment.get("hypo_bank")),
            ("Service Record", payment.get("service_record")),
            ("PUC", payment.get("puc")),
            ("Memo", payment.get("memo")),
            ("Memo Amount", _format_money(payment.get("memo_amount"))),
            ("Memo Paid", payment.get("memo_paid")),
            ("MV Tax", _format_money(payment.get("mv_tax"))),
            ("RMA", payment.get("rma")),
            ("Taxi/Private", payment.get("taxi_private")),
            ("Other NOC", payment.get("other_noc")),
            ("Blacklist", payment.get("blacklist")),
            ("RTO Status", payment.get("rto_status")),
        ],
    )

    canvas.pairs(
        "Insurance Details",
        [
            ("Online Insurance", payment.get("online_insurance")),
            ("Insurance Type", payment.get("insurance_type")),
            ("CP/ZD Company", payment.get("cp_zd_company")),
            ("TP Company", payment.get("tp_company")),
            ("CP/ZD Date", payment.get("cp_zd_date")),
            ("TP Date", payment.get("tp_date")),
            ("IDV", _format_money(payment.get("idv"))),
            ("NCB", _format_money(payment.get("ncb"))),
            ("Premium", _format_money(payment.get("premium"))),
        ],
    )

    canvas.pairs(
        "Payment Details",
        [
            ("Deal", _format_money(payment.get("deal"))),
            (
                "Deal Without Comm.",
                _format_money(payment.get("deal_without_commission")),
            ),
            ("Refurb Cost", _format_money(payment.get("refurb_cost"))),
            ("Service Charge", _format_money(payment.get("service_charge"))),
            ("Token", _format_money(payment.get("token"))),
            ("TCS", _format_money(payment.get("tcs"))),
            ("Cash", _format_money(payment.get("cash"))),
            ("GST", _format_money(payment.get("gst"))),
            ("Loan", _format_money(payment.get("loan"))),
            ("Tax", _format_money(payment.get("tax"))),
            ("Less", _format_money(payment.get("less"))),
            ("RCD", _format_money(payment.get("rcd"))),
            ("Hold", _format_money(payment.get("hold"))),
            ("Commission", _format_money(payment.get("commission"))),
            (
                "Deal With Comm.",
                _format_money(payment.get("deal_with_commission")),
            ),
            ("CH/RTGS", _format_money(payment.get("ch_rtgs"))),
            ("Total Payble", _format_money(payment.get("total_payble"))),
            ("Created By", payment.get("payment_created_by")),
            ("Created At", payment.get("payment_created_at")),
            ("Modified By", payment.get("payment_modified_by")),
        ],
    )
    canvas.paragraph("Payment Remarks", payment.get("payment_remarks"))
    canvas.paragraph("Lead Remarks", payment.get("lead_remarks"))
    canvas.finish()
    return _build_pdf(canvas.pages)
