from __future__ import annotations

import re
import base64
import shutil
import subprocess
import tempfile
import zipfile
from io import BytesIO
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree as ET

import httpx

from app.core.config import settings

TEXT_EXTENSIONS = {"txt", "md", "csv", "json", "log"}
WORD_EXTENSIONS = {"doc", "docx"}
PDF_EXTENSIONS = {"pdf"}
HTML_EXTENSIONS = {"html", "htm"}
SPREADSHEET_EXTENSIONS = {"xls", "xlsx"}
PRESENTATION_EXTENSIONS = {"ppt", "pptx"}
ODF_EXTENSIONS = {"odt", "ods", "odp"}
STRUCTURED_TEXT_EXTENSIONS = {"tsv", "yaml", "yml"}
IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "bmp", "tif", "tiff"}
_THINK_TAG_RE = re.compile(r"<think>.*?</think>\s*", re.S)


class _ReadableHtmlParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._skip_depth = 0
        self._parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "noscript"}:
            self._skip_depth += 1
            return
        if tag in {"p", "div", "section", "article", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6", "br"}:
            self._parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"} and self._skip_depth:
            self._skip_depth -= 1
            return
        if tag in {"p", "div", "section", "article", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6"}:
            self._parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self._skip_depth and data:
            self._parts.append(data)

    def text(self) -> str:
        lines = []
        for line in "".join(self._parts).splitlines():
            clean = re.sub(r"\s+", " ", line).strip()
            if clean:
                lines.append(clean)
        return "\n".join(lines)


class DocumentParser:
    _WORD_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    _READABLE_RUN_RE = re.compile(
        r"[\u4e00-\u9fffA-Za-z0-9，。！？；：、,.!?;:()\[\]《》“”\"'`~+\-*/=<>@#%&￥$ \t]{4,}"
    )

    def parse_bytes(self, content: bytes, file_ext: str) -> str:
        ext = (file_ext or "").lower().lstrip(".")
        if ext in TEXT_EXTENSIONS | STRUCTURED_TEXT_EXTENSIONS:
            return self._parse_plain_text(content)
        if ext == "docx":
            return self._parse_docx(content)
        if ext == "doc":
            return self._parse_legacy_doc(content)
        if ext == "pdf":
            return self._parse_pdf(content)
        if ext in HTML_EXTENSIONS:
            return self._parse_html(content)
        if ext == "rtf":
            return self._parse_rtf(content)
        if ext == "xml":
            return self._parse_xml(content)
        if ext == "xlsx":
            return self._parse_xlsx(content)
        if ext == "xls":
            return self._parse_xls(content)
        if ext == "pptx":
            return self._parse_pptx(content)
        if ext == "ppt":
            return self._parse_legacy_office(content, ext)
        if ext in ODF_EXTENSIONS:
            return self._parse_odf(content)
        if ext in IMAGE_EXTENSIONS:
            return self._parse_image(content, ext)
        raise ValueError(f"document_format_not_supported:{ext or 'unknown'}")

    def _parse_plain_text(self, content: bytes) -> str:
        for encoding in ("utf-8-sig", "gb18030", "utf-16"):
            try:
                text = content.decode(encoding, errors="strict")
            except UnicodeDecodeError:
                continue
            cleaned = text.replace("\ufeff", "").strip()
            if cleaned and self._meaningful_char_count(cleaned) >= 2:
                return text
        raise ValueError("document_encoding_not_supported")

    def _parse_docx(self, content: bytes) -> str:
        try:
            archive = zipfile.ZipFile(BytesIO(content))
        except zipfile.BadZipFile as exc:
            raise ValueError("document_docx_invalid") from exc

        xml_names = [
            name
            for name in archive.namelist()
            if name == "word/document.xml"
            or (
                name.startswith("word/")
                and name.endswith(".xml")
                and any(part in name for part in ("header", "footer", "footnotes", "endnotes"))
            )
        ]
        xml_names.sort(key=lambda name: (name != "word/document.xml", name))

        paragraphs: list[str] = []
        for name in xml_names:
            try:
                root = ET.fromstring(archive.read(name))
            except ET.ParseError:
                continue
            for para in root.iter(f"{self._WORD_NS}p"):
                parts: list[str] = []
                for node in para.iter():
                    if node.tag == f"{self._WORD_NS}t" and node.text:
                        parts.append(node.text)
                    elif node.tag == f"{self._WORD_NS}tab":
                        parts.append("\t")
                    elif node.tag == f"{self._WORD_NS}br":
                        parts.append("\n")
                text = "".join(parts).strip()
                if text:
                    paragraphs.append(text)

        text = "\n".join(paragraphs).strip()
        if not text:
            raise ValueError("document_empty")
        return text

    def _parse_legacy_doc(self, content: bytes) -> str:
        if content.startswith(b"PK"):
            return self._parse_docx(content)

        converted = self._convert_with_office_tools(content, "doc")
        if converted.strip():
            return converted

        extracted = self._extract_readable_text_runs(content)
        if extracted.strip():
            return extracted
        raise ValueError("document_legacy_doc_not_supported")

    def _parse_legacy_office(self, content: bytes, ext: str) -> str:
        converted = self._convert_with_office_tools(content, ext)
        if converted.strip():
            return converted
        extracted = self._extract_readable_text_runs(content)
        if extracted.strip():
            return extracted
        raise ValueError(f"document_legacy_{ext}_not_supported")

    def _parse_pdf(self, content: bytes) -> str:
        if not content.startswith(b"%PDF"):
            raise ValueError("document_pdf_invalid")

        text = self._parse_pdf_with_pypdf(content)
        if not text.strip():
            text = self._parse_pdf_with_pymupdf(content)
        if not text.strip():
            text = self._parse_pdf_with_model_ocr(content)
        if not text.strip():
            raise ValueError("document_pdf_text_empty")
        return text

    def _parse_pdf_with_pypdf(self, content: bytes) -> str:
        try:
            from pypdf import PdfReader
        except ImportError:
            return ""
        try:
            reader = PdfReader(BytesIO(content))
            pages = []
            for page in reader.pages:
                pages.append(page.extract_text() or "")
        except Exception:
            return ""
        return self._clean_extracted_text("\n".join(pages))

    def _parse_pdf_with_pymupdf(self, content: bytes) -> str:
        try:
            import fitz
        except ImportError:
            return ""
        try:
            with fitz.open(stream=content, filetype="pdf") as doc:
                pages = [page.get_text("text") for page in doc]
        except Exception:
            return ""
        return self._clean_extracted_text("\n".join(pages))

    def _parse_pdf_with_model_ocr(self, content: bytes) -> str:
        if not settings.document_ocr_configured:
            return ""
        images = self._render_pdf_pages_for_ocr(content)
        if not images:
            return ""
        return self._ocr_images_with_model(images, source_label="PDF")

    def _render_pdf_pages_for_ocr(self, content: bytes) -> list[tuple[str, bytes]]:
        try:
            import fitz
        except ImportError:
            return []
        max_pages = max(1, min(int(settings.document_ocr_max_pages or 3), 10))
        images: list[tuple[str, bytes]] = []
        try:
            with fitz.open(stream=content, filetype="pdf") as doc:
                for page in list(doc)[:max_pages]:
                    pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
                    images.append(("image/png", pixmap.tobytes("png")))
        except Exception:
            return []
        return images

    def _parse_image(self, content: bytes, ext: str) -> str:
        mime_type = self._image_mime_type(content, ext)
        if not mime_type:
            raise ValueError("document_image_invalid")
        text = self._ocr_images_with_model([(mime_type, content)], source_label="image")
        if not text.strip():
            raise ValueError("document_ocr_empty")
        return text

    def _image_mime_type(self, content: bytes, ext: str) -> str:
        normalized = str(ext or "").lower().lstrip(".")
        if normalized == "png" and content.startswith(b"\x89PNG\r\n\x1a\n"):
            return "image/png"
        if normalized in {"jpg", "jpeg"} and content.startswith(b"\xff\xd8\xff"):
            return "image/jpeg"
        if normalized == "webp" and content.startswith(b"RIFF") and content[8:12] == b"WEBP":
            return "image/webp"
        if normalized == "bmp" and content.startswith(b"BM"):
            return "image/bmp"
        if normalized in {"tif", "tiff"} and (content.startswith(b"II*\x00") or content.startswith(b"MM\x00*")):
            return "image/tiff"
        return ""

    def _ocr_images_with_model(self, images: list[tuple[str, bytes]], source_label: str) -> str:
        if not settings.document_ocr_configured:
            raise ValueError("document_ocr_not_configured")
        parts: list[dict[str, object]] = [
            {
                "type": "text",
                "text": (
                    "请对上传的校园资料图片做 OCR，只提取图片中真实存在的正文。"
                    "保持原有段落顺序，表格可转成 Markdown 表格或用制表符分隔。"
                    "不要补充、推测或编造图片中没有的内容；如果没有可识别文字，只返回空字符串。"
                ),
            }
        ]
        for mime_type, data in images:
            encoded = base64.b64encode(data).decode("ascii")
            parts.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:{mime_type};base64,{encoded}"},
                }
            )

        payload = {
            "model": str(settings.document_ocr_model or "").strip(),
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "你是严谨的 OCR 文档解析器，任务是把图片中的可见文字转成可入库的 Markdown 文本。"
                        "只输出识别结果，不输出解释、免责声明或无关寒暄。"
                    ),
                },
                {"role": "user", "content": parts},
            ],
            "temperature": 0,
            "max_tokens": 4096,
        }
        headers = {"Authorization": f"Bearer {settings.document_ocr_api_key_effective}"}
        try:
            with httpx.Client(timeout=max(5, int(settings.document_ocr_timeout_seconds or 45))) as client:
                response = client.post(
                    f"{settings.document_ocr_base_url_effective.rstrip('/')}/chat/completions",
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
                data = response.json()
        except Exception as exc:
            raise ValueError("document_ocr_failed") from exc

        raw = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        if isinstance(raw, list):
            raw = "\n".join(str(item.get("text", "")) if isinstance(item, dict) else str(item) for item in raw)
        text = self._clean_extracted_text(_THINK_TAG_RE.sub("", str(raw or "")).strip())
        if not text:
            raise ValueError(f"document_{source_label.lower()}_ocr_empty")
        return text

    def _parse_html(self, content: bytes) -> str:
        decoded = self._decode_text(content)
        parser = _ReadableHtmlParser()
        try:
            parser.feed(decoded)
            parser.close()
        except Exception as exc:
            raise ValueError("document_html_invalid") from exc
        text = parser.text()
        if not text.strip():
            raise ValueError("document_empty")
        return text

    def _parse_rtf(self, content: bytes) -> str:
        text = self._decode_text(content)

        def replace_unicode(match: re.Match[str]) -> str:
            codepoint = int(match.group(1))
            if codepoint < 0:
                codepoint += 65536
            try:
                return chr(codepoint)
            except ValueError:
                return ""

        text = re.sub(r"\\u(-?\d+)\??", replace_unicode, text)
        text = re.sub(
            r"\\'([0-9a-fA-F]{2})",
            lambda match: bytes.fromhex(match.group(1)).decode("cp1252", errors="ignore"),
            text,
        )
        text = re.sub(r"\\[a-zA-Z]+-?\d* ?", " ", text)
        text = text.replace("{", " ").replace("}", " ").replace("\\", " ")
        cleaned = self._clean_extracted_text(text)
        if not cleaned:
            raise ValueError("document_empty")
        return cleaned

    def _parse_xml(self, content: bytes) -> str:
        decoded = self._decode_text(content)
        try:
            root = ET.fromstring(decoded)
        except ET.ParseError as exc:
            raise ValueError("document_xml_invalid") from exc
        text = self._clean_extracted_text("\n".join(root.itertext()))
        if not text:
            raise ValueError("document_empty")
        return text

    def _parse_xlsx(self, content: bytes) -> str:
        try:
            archive = zipfile.ZipFile(BytesIO(content))
        except zipfile.BadZipFile as exc:
            raise ValueError("document_xlsx_invalid") from exc

        shared_strings: list[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            try:
                root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
                for item in root.iter():
                    if item.tag.endswith("}si") or item.tag == "si":
                        shared_strings.append("".join(item.itertext()).strip())
            except ET.ParseError:
                shared_strings = []

        rows: list[str] = []
        sheet_names = sorted(name for name in archive.namelist() if name.startswith("xl/worksheets/sheet") and name.endswith(".xml"))
        for sheet_index, name in enumerate(sheet_names, start=1):
            try:
                root = ET.fromstring(archive.read(name))
            except ET.ParseError:
                continue
            rows.append(f"## Sheet {sheet_index}")
            for row in root.iter():
                if not (row.tag.endswith("}row") or row.tag == "row"):
                    continue
                cells = []
                for cell in list(row):
                    if not (cell.tag.endswith("}c") or cell.tag == "c"):
                        continue
                    value = self._extract_xlsx_cell_value(cell, shared_strings)
                    if value:
                        cells.append(value)
                if cells:
                    rows.append("\t".join(cells))

        text = self._clean_extracted_text("\n".join(rows))
        if not text:
            raise ValueError("document_empty")
        return text

    def _extract_xlsx_cell_value(self, cell: ET.Element, shared_strings: list[str]) -> str:
        cell_type = cell.attrib.get("t", "")
        if cell_type == "inlineStr":
            return "".join(cell.itertext()).strip()
        value_node = next((node for node in cell if node.tag.endswith("}v") or node.tag == "v"), None)
        value = (value_node.text or "").strip() if value_node is not None else ""
        if cell_type == "s" and value.isdigit():
            index = int(value)
            if 0 <= index < len(shared_strings):
                return shared_strings[index]
        return value

    def _parse_xls(self, content: bytes) -> str:
        try:
            import xlrd
        except ImportError:
            converted = self._convert_with_office_tools(content, "xls")
            if converted.strip():
                return converted
            raise ValueError("document_xls_dependency_missing")
        try:
            workbook = xlrd.open_workbook(file_contents=content)
        except Exception as exc:
            converted = self._convert_with_office_tools(content, "xls")
            if converted.strip():
                return converted
            raise ValueError("document_xls_invalid") from exc
        rows: list[str] = []
        for sheet in workbook.sheets():
            rows.append(f"## {sheet.name}")
            for row_index in range(sheet.nrows):
                values = []
                for value in sheet.row_values(row_index):
                    text = str(value).strip()
                    if text:
                        values.append(text)
                if values:
                    rows.append("\t".join(values))
        text = self._clean_extracted_text("\n".join(rows))
        if not text:
            raise ValueError("document_empty")
        return text

    def _parse_pptx(self, content: bytes) -> str:
        try:
            archive = zipfile.ZipFile(BytesIO(content))
        except zipfile.BadZipFile as exc:
            raise ValueError("document_pptx_invalid") from exc
        slide_names = sorted(name for name in archive.namelist() if name.startswith("ppt/slides/slide") and name.endswith(".xml"))
        slides: list[str] = []
        for index, name in enumerate(slide_names, start=1):
            try:
                root = ET.fromstring(archive.read(name))
            except ET.ParseError:
                continue
            texts = [node.text.strip() for node in root.iter() if node.tag.endswith("}t") and node.text and node.text.strip()]
            if texts:
                slides.append(f"## Slide {index}\n" + "\n".join(texts))
        text = self._clean_extracted_text("\n".join(slides))
        if not text:
            raise ValueError("document_empty")
        return text

    def _parse_odf(self, content: bytes) -> str:
        try:
            archive = zipfile.ZipFile(BytesIO(content))
        except zipfile.BadZipFile as exc:
            raise ValueError("document_odf_invalid") from exc
        if "content.xml" not in archive.namelist():
            raise ValueError("document_odf_invalid")
        try:
            root = ET.fromstring(archive.read("content.xml"))
        except ET.ParseError as exc:
            raise ValueError("document_odf_invalid") from exc
        lines: list[str] = []
        for node in root.iter():
            tag = node.tag.rsplit("}", 1)[-1]
            if tag in {"h", "p", "table-cell"}:
                text = " ".join(part.strip() for part in node.itertext() if part and part.strip())
                if text:
                    lines.append(text)
        text = self._clean_extracted_text("\n".join(lines))
        if not text:
            raise ValueError("document_empty")
        return text

    def _convert_with_office_tools(self, content: bytes, ext: str) -> str:
        tmp_root = Path(__file__).resolve().parents[3] / "data" / "tmp"
        tmp_root.mkdir(parents=True, exist_ok=True)
        safe_ext = re.sub(r"[^a-z0-9]", "", ext.lower()) or "bin"
        with tempfile.TemporaryDirectory(prefix="campus_doc_", dir=tmp_root) as tmp_dir:
            input_path = Path(tmp_dir) / f"input.{safe_ext}"
            input_path.write_bytes(content)

            tool_names = {
                "doc": ("antiword", "catdoc"),
                "xls": ("xls2csv",),
                "ppt": ("catppt",),
            }.get(safe_ext, ())
            for name in tool_names:
                executable = shutil.which(name)
                if not executable:
                    continue
                text = self._run_text_command([executable, str(input_path)])
                if text.strip():
                    return text

            for name in ("libreoffice", "soffice"):
                executable = shutil.which(name)
                if not executable:
                    continue
                subprocess.run(
                    [
                        executable,
                        "--headless",
                        "--convert-to",
                        "txt:Text",
                        "--outdir",
                        str(tmp_dir),
                        str(input_path),
                    ],
                    check=False,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=25,
                )
                output_path = Path(tmp_dir) / "input.txt"
                if output_path.exists():
                    text = self._decode_text(output_path.read_bytes())
                    if text.strip():
                        return text
        return ""

    def _run_text_command(self, command: list[str]) -> str:
        try:
            result = subprocess.run(
                command,
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=20,
            )
        except (OSError, subprocess.SubprocessError):
            return ""
        return self._decode_text(result.stdout)

    def _decode_text(self, data: bytes) -> str:
        for encoding in ("utf-8-sig", "gb18030", "utf-16le"):
            try:
                return data.decode(encoding)
            except UnicodeDecodeError:
                continue
        return data.decode("utf-8", errors="ignore")

    def _clean_extracted_text(self, value: str) -> str:
        lines = []
        for line in str(value or "").replace("\r\n", "\n").replace("\r", "\n").split("\n"):
            clean = re.sub(r"[ \t]+", " ", line).strip()
            if clean:
                lines.append(clean)
        return "\n".join(lines)

    def _extract_readable_text_runs(self, content: bytes) -> str:
        candidates = []
        for encoding in ("utf-16le", "gb18030", "utf-8"):
            decoded = content.decode(encoding, errors="ignore")
            runs = [self._clean_run(item) for item in self._READABLE_RUN_RE.findall(decoded)]
            text = "\n".join(item for item in runs if self._is_meaningful_run(item))
            score = sum(self._meaningful_char_count(item) for item in runs)
            candidates.append((score, text))

        score, text = max(candidates, key=lambda item: item[0], default=(0, ""))
        if score < 30:
            return ""
        return text.strip()

    def _clean_run(self, value: str) -> str:
        text = re.sub(r"\s+", " ", value.replace("\x00", " ")).strip()
        return text

    def _is_meaningful_run(self, value: str) -> bool:
        if len(value) < 4:
            return False
        return self._meaningful_char_count(value) >= max(4, int(len(value) * 0.5))

    def _meaningful_char_count(self, value: str) -> int:
        return sum(1 for char in value if "\u4e00" <= char <= "\u9fff" or char.isalnum())


document_parser = DocumentParser()
