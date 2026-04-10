class DocumentParser:
    def parse_bytes(self, content: bytes, file_ext: str) -> str:
        ext = (file_ext or "").lower()
        if ext in {"txt", "md", "csv", "json", "log"}:
            return content.decode("utf-8-sig", errors="strict")
        raise ValueError(f"document_format_not_supported:{ext or 'unknown'}")


document_parser = DocumentParser()
