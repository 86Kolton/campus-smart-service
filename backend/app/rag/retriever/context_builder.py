class ContextBuilder:
    def build(self, items: list[dict], limit: int = 6) -> list[str]:
        return [item.get("text", "") for item in items[:limit] if item.get("text")]


context_builder = ContextBuilder()

