class FlowEngine:
    def __init__(self, flow: dict):
        self.flow = flow

    def get_block(self, block_id: str):
        return self.flow["blocks"].get(block_id)

    def next_block(self, current_block: dict, user_input: str):
        # Determinista: prioriza ramas declaradas; si no, usa el campo next/next_map.
        next_map = current_block.get("next_map")
        if isinstance(next_map, dict):
            if user_input in next_map:
                return next_map[user_input]
            if "default" in next_map:
                return next_map["default"]
            # si no hay match, toma la primera
            return next(iter(next_map.values()))
        branches = current_block.get("branches")
        if branches:
            if isinstance(branches, dict):
                if user_input in branches:
                    return branches[user_input]
                if "default" in branches:
                    return branches["default"]
                # sin lógica de IA: tomar la primera rama declarada
                return next(iter(branches.values()))
        return current_block.get("next")

    def choose_text(self, node: dict, lang: str, default_lang: str) -> str:
        text = node.get("text")
        if isinstance(text, dict):
            return text.get(lang) or text.get(default_lang) or next(iter(text.values()))
        return text or ""
