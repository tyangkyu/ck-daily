from __future__ import annotations

import re
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape


def _plain_lines(markdown: str) -> list[str]:
    lines = []
    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        line = re.sub(r"!\[[^\]]*\]\([^)]+\)", "[히어로 비주얼]", line)
        line = re.sub(r"\*\*([^*]+)\*\*", r"\1", line)
        line = line.lstrip("#> -")
        if line:
            lines.append(line)
    return lines


def write_docx(path: Path, markdown: str) -> None:
    lines = _plain_lines(markdown)
    paragraphs = "\n".join(
        f"<w:p><w:r><w:t>{xml_escape(line)}</w:t></w:r></w:p>"
        for line in lines
    )
    document_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    {paragraphs}
    <w:sectPr>
      <w:pgSz w:w="11906" w:h="16838"/>
      <w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"/>
    </w:sectPr>
  </w:body>
</w:document>
"""
    content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>
"""
    rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types)
        archive.writestr("_rels/.rels", rels)
        archive.writestr("word/document.xml", document_xml)


def _pdf_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def write_pdf(path: Path, markdown: str) -> None:
    lines = _plain_lines(markdown)[:42]
    text_ops = ["BT", "/F1 11 Tf", "50 790 Td", "14 TL"]
    for index, line in enumerate(lines):
        escaped = _pdf_escape(line[:110])
        if index == 0:
            text_ops.append(f"({escaped}) Tj")
        else:
            text_ops.append(f"T* ({escaped}) Tj")
    text_ops.append("ET")
    stream = "\n".join(text_ops).encode("utf-8")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream",
    ]

    chunks = [b"%PDF-1.4\n"]
    offsets = [0]
    for number, obj in enumerate(objects, start=1):
        offsets.append(sum(len(chunk) for chunk in chunks))
        chunks.append(f"{number} 0 obj\n".encode("ascii") + obj + b"\nendobj\n")
    xref_offset = sum(len(chunk) for chunk in chunks)
    xref = [f"xref\n0 {len(objects) + 1}\n".encode("ascii"), b"0000000000 65535 f \n"]
    for offset in offsets[1:]:
        xref.append(f"{offset:010d} 00000 n \n".encode("ascii"))
    trailer = (
        b"trailer\n"
        + f"<< /Size {len(objects) + 1} /Root 1 0 R >>\n".encode("ascii")
        + b"startxref\n"
        + str(xref_offset).encode("ascii")
        + b"\n%%EOF\n"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"".join(chunks + xref + [trailer]))
