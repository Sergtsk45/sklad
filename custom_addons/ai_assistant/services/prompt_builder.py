_SYSTEM_PROMPT = (
    "Ты — встроенный AI-консультант системы Odoo 19.\n"
    "Твоя задача — помогать пользователям разобраться"
    " в интерфейсе и возможностях Odoo.\n"
    "\n"
    "Правила:\n"
    "- Отвечай только на вопросы об использовании"
    " интерфейса Odoo и его функциях.\n"
    "- Давай короткие пошаговые инструкции.\n"
    "- Используй термины интерфейса на языке пользователя"
    " (преимущественно на русском).\n"
    "- Не выдумывай кнопки, поля или пути в меню —"
    " опирайся только на предоставленную документацию и контекст.\n"
    "- Если не уверен в ответе — скажи об этом прямо.\n"
    "- Если функция недоступна пользователю — предложи,"
    " где её включить или к кому обратиться.\n"
    "- Не выполняй действия от имени пользователя.\n"
    "- Не обещай автоматических изменений в системе."
)

_SAFETY_RULES = (
    "Ограничения:\n"
    "- Отвечай только на вопросы, связанные с работой в Odoo.\n"
    "- Не давай советов по безопасности, финансам или юридическим вопросам.\n"
    "- Не обещай выполнить действия автоматически.\n"
    "- Если вопрос вне твоей компетенции — вежливо сообщи об этом."
)


class PromptBuilder:

    def build_system_prompt(self, override=None):
        if override:
            return override
        return _SYSTEM_PROMPT

    def build_safety_rules(self):
        return _SAFETY_RULES

    def build_context_block(self, context):
        if not context:
            return ''
        parts = []
        if context.get('module'):
            parts.append(f"Модуль: {context['module']}")
        if context.get('action'):
            parts.append(f"Раздел: {context['action']}")
        if context.get('model'):
            parts.append(f"Модель данных: {context['model']}")
        if context.get('view_type'):
            parts.append(f"Тип представления: {context['view_type']}")
        if context.get('lang'):
            parts.append(f"Язык: {context['lang']}")
        groups = context.get('user_groups') or []
        if groups:
            parts.append(f"Группы пользователя: {', '.join(groups[:5])}")
        if not parts:
            return ''
        lines = ['Текущий контекст экрана пользователя:']
        lines += [f'- {p}' for p in parts]
        return '\n'.join(lines)

    def build_knowledge_block(self, snippets):
        if not snippets:
            return ''
        lines = ['Справочная документация по Odoo:']
        for snippet in snippets:
            topic = snippet.get('topic', '')
            content = snippet.get('content', '')
            if topic and content:
                lines.append(f'\n### {topic}\n{content}')
        return '\n'.join(lines)

    def build_messages(self, system_prompt, history, user_message):
        messages = [{'role': 'system', 'content': system_prompt}]
        for item in history:
            role = item.get('role', '')
            content = item.get('content', '')
            if role in ('user', 'assistant') and content:
                messages.append({'role': role, 'content': content})
        messages.append({'role': 'user', 'content': user_message})
        return messages
