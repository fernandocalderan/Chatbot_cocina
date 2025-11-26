from app.observability import metrics


class FlowEngine:
    def __init__(self, flow: dict, context: dict | None = None):
        """
        flow: dict con la definición del flujo (blocks, start_block, etc.)
        context: diccionario de variables de sesión (state["vars"]) que usaremos
                 para evaluar condiciones tipo "tipo_proyecto in [...]".
        """
        self.flow = flow
        # Guardamos referencia al dict de contexto (no una copia) para que
        # los cambios en state["vars"] se vean aquí sin recrear el engine.
        self.context = context or {}

    def set_context(self, context: dict | None):
        """Permite actualizar el contexto si fuera necesario."""
        self.context = context or {}

    def get_block(self, block_id: str):
        return self.flow["blocks"].get(block_id)

    def next_block(self, current_block: dict, user_input: str | None):
        """
        Lógica determinista de transición:
        - Si el bloque es de tipo 'condition', evalúa la lista de condiciones.
        - Si tiene 'next_map', lo usa con user_input.
        - Si tiene 'branches', lo usa con user_input.
        - Si no, cae al 'next' simple.
        """
        if not current_block:
            return None

        block_type = current_block.get("type")
        tenant_id = (self.context or {}).get("tenant_id") or "unknown"
        metrics.inc_counter(
            "flow_blocks_processed_total",
            {"tenant_id": tenant_id, "block_type": block_type or "unknown"},
        )

        # 1) Bloques de condición (condition) -> usan self.context
        if block_type == "condition":
            ctx = self.context or {}
            conditions = current_block.get("conditions", [])
            for cond in conditions:
                expr = cond.get("if") or ""
                next_id = cond.get("next")
                # Si no hay next_id, ignoramos esa condición
                if not next_id:
                    continue
                # Si la condición está vacía, la consideramos como True
                if not expr:
                    return next_id
                try:
                    # Evaluamos en un entorno seguro: sin globals, solo ctx
                    if eval(expr, {}, ctx):
                        return next_id
                except Exception:
                    # Si falla la eval, saltamos a la siguiente condición
                    continue
            # Si ninguna condición matchea, usamos el 'next' del bloque si existe
            return current_block.get("next")

        # 2) next_map explícito
        next_map = current_block.get("next_map")
        if isinstance(next_map, dict):
            if user_input in next_map:
                return next_map[user_input]
            if "default" in next_map:
                return next_map["default"]
            # si no hay match, toma la primera
            return next(iter(next_map.values()))

        # 3) branches (heredado)
        branches = current_block.get("branches")
        if isinstance(branches, dict) and branches:
            if user_input in branches:
                return branches[user_input]
            if "default" in branches:
                return branches["default"]
            # sin IA: tomar la primera rama declarada
            return next(iter(branches.values()))

        # 4) Fallback: next simple
        return current_block.get("next")

    def choose_text(self, node: dict, lang: str, default_lang: str) -> str:
        text = node.get("text")
        if isinstance(text, dict):
            return text.get(lang) or text.get(default_lang) or next(iter(text.values()))
        return text or ""
