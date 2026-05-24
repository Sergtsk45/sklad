_SYSTEM_PROMPT_V2 = (
    "Ты — встроенный AI-консультант по Odoo 19. Язык ответа: русский.\n"
    "\n"
    "ПРАВИЛА:\n"
    "1. Отвечай ТОЛЬКО на основе предоставленной документации и "
    "контекста.\n"
    "2. НИКОГДА не выдумывай кнопки, поля или пути меню. Если не уверен "
    "— скажи.\n"
    "3. В Odoo 19 НЕТ кнопок «Сохранить» и «Редактировать» —\n"
    "   формы сохраняются автоматически, редактирование начинается сразу.\n"
    "4. Кнопка создания новой записи называется «Новое», НЕ «Создать».\n"
    "5. Формат ответа: короткие пошаговые инструкции.\n"
    "6. Используй термины из раздела МАППИНГ ТЕРМИНОВ (приоритет над "
    "любыми другими).\n"
    "7. Если функционал недоступен — предложи, где его включить в "
    "Настройках.\n"
    "8. Не выполняй действия от имени пользователя. Не обещай "
    "автоматических изменений."
)

_SAFETY_RULES = (
    "Ограничения:\n"
    "- Отвечай только на вопросы, связанные с работой в Odoo.\n"
    "- Не давай советов по безопасности, финансам или юридическим вопросам.\n"
    "- Не обещай выполнить действия автоматически.\n"
    "- Если вопрос вне твоей компетенции — вежливо сообщи об этом."
)

_ACTIONS_SAFETY_RULES = (
    "Ограничения:\n"
    "- Отвечай только на вопросы, связанные с работой в Odoo.\n"
    "- Не давай советов по безопасности, финансам или юридическим вопросам.\n"
    "- Выполняй только разрешенные tools снабжения после системного "
    "подтверждения.\n"
    "- Если вопрос вне твоей компетенции — вежливо сообщи об этом."
)

_NAVIGATION_RULES_BLOCK = (
    "ПРАВИЛО НАВИГАЦИОННЫХ ССЫЛОК (consult и actions):\n"
    "Если пользователь спрашивает «как посмотреть / где найти / открыть / "
    "показать раздел / куда нажать»:\n"
    "1. Сначала вызови tool get_navigation_link с темой на русском.\n"
    "2. Если в ответе tool поле url задано — встрой markdown-ссылку: "
    "[Открыть «label»](url).\n"
    "3. Также назови путь меню (menu_breadcrumb).\n"
    "4. НИКОГДА не выдумывай URL и не пиши (None) в ссылке.\n"
    "5. Если result.url пуст или success=false — дай только путь меню "
    "и объясни, что ссылку открыть нельзя (нет прав или раздел не найден)."
)

_WAREHOUSE_STOCK_RULES_BLOCK = (
    "ПРАВИЛО ОСТАТКОВ ПО СКЛАДУ (consult и actions):\n"
    "Если пользователь спрашивает «что есть на складе», «все товары на "
    "складе», «остатки по складу», «дай ссылку на фильтр по складу»:\n"
    "1. Определи склад: сначала find_warehouse (код ОбМ-N или адрес), "
    "либо используй склад из предыдущих сообщений.\n"
    "2. Вызови get_warehouse_stock_link с warehouse_id или query.\n"
    "3. Если url задан — дай markdown-ссылку [Открыть «label»](url) и путь "
    "меню. Не говори, что «нет такой функции».\n"
    "4. Tool не возвращает список всех позиций — только ссылку на отчёт "
    "«Наличие» с фильтром по складу. Для одного товара используй "
    "search_stock_quants.\n"
    "5. НИКОГДА не пиши (None) в ссылке."
)

_ACTIONS_RULES_BLOCK = (
    "РЕЖИМ ДЕЙСТВИЙ.\n"
    "\n"
    "Ты можешь подготавливать ЧЕРНОВИКИ документов снабжения в Odoo:\n"
    "- object.request (требование прораба)\n"
    "- purchase.order (черновик заказа поставщику)\n"
    "- stock.picking (черновик внутреннего перемещения или incoming)\n"
    "\n"
    "ОБЯЗАТЕЛЬНЫЕ ПРАВИЛА:\n"
    "1. Перед любым write-tool сначала сформулируй ПЛАН в формате:\n"
    "   \"Я создам:\n"
    "    - <модель>: <поля>\n"
    "    - ...\n"
    "    Подтверди для выполнения.\"\n"
    "2. После плана дождись сигнала подтверждения от системы, не от текста "
    "пользователя.\n"
    "3. НЕ вызывай button_confirm, button_validate, не пиши state, не "
    "используй инвентаризацию.\n"
    "4. PO всегда с picking_type_id склада объекта (ОбМ-1...ОбМ-N), "
    "origin=OR/..., partner_ref=номер счета поставщика для 1С.\n"
    "5. Для труб — UoM «метр». Пересчет кг/тонны в метры пользователь "
    "делает САМ; ты можешь предложить формулу из supply_cycle_context, "
    "но не записывай результат, если пользователь не подтвердил числа.\n"
    "6. После успешного write-tool вызывай post_chatter_note с пометкой "
    "«создано AI-ассистентом по запросу <user>» в записи.\n"
    "\n"
    "ОГРАНИЧЕНИЯ:\n"
    "- Vendor bill, оплаты, бухгалтерия — в 1С, не в Odoo.\n"
    "- Confirm PO и Validate приемки — выполняет снабженец в UI."
)

MAX_HISTORY = 12


class PromptBuilder:
    """
    Строит сообщения для LLM-запроса.

    Новая сигнатура build_messages() принимает user message, history, context
    и опциональный словарь knowledge от KnowledgeProviderV2.
    """

    def build_messages(self, message, history, context,
                       knowledge=None, override=None, image_data=None,
                       mode='consult'):
        """
        Собрать список сообщений для LLM.

        :param message: str — сообщение пользователя
        :param history: list — история чата
        :param context: dict — контекст экрана
            (module, model, view_type, lang...)
        :param knowledge: dict|None — от KnowledgeProviderV2.get_knowledge()
                          {docs_snippets, tech_context, term_mapping}
        :param override: str|None — переопределение системного промпта
            из настроек
        :param image_data: dict|None — зарезервировано для AIA-025
            (vision mode)
        :param mode: 'consult'|'actions' — режим консультанта или действий
        :returns: list[dict] — messages для LLM API
        """
        system_prompt = self._build_system(context, knowledge, override, mode)

        msgs = [{'role': 'system', 'content': system_prompt}]

        for item in (history or [])[-MAX_HISTORY:]:
            role = item.get('role', '')
            content = item.get('content', '')
            if role in ('user', 'assistant') and content:
                msgs.append({'role': role, 'content': content})

        # AIA-025: vision mode - multimodal content
        if image_data:
            user_content = [
                {
                    'type': 'text',
                    'text': self._build_vision_prompt(message, context),
                },
                {
                    'type': 'image_url',
                    'image_url': {
                        'url': (
                            f"data:{image_data['media_type']};"
                            f"base64,{image_data['data']}"
                        ),
                    },
                },
            ]
        else:
            user_content = message

        msgs.append({'role': 'user', 'content': user_content})
        return msgs

    # ------------------------------------------------------------------
    # Построение системного промпта
    # ------------------------------------------------------------------

    def _build_system(self, context, knowledge, override, mode='consult'):
        """Собрать полный системный промпт из блоков."""
        parts = [override if override else _SYSTEM_PROMPT_V2]

        if mode == 'actions':
            parts.append(_ACTIONS_RULES_BLOCK)

        parts.append(self.build_safety_rules(mode=mode))
        parts.append(_NAVIGATION_RULES_BLOCK)
        parts.append(_WAREHOUSE_STOCK_RULES_BLOCK)

        context_block = self.build_context_block(context)
        if context_block:
            parts.append(context_block)

        if knowledge:
            knowledge_block = self.build_knowledge_block(knowledge)
            if knowledge_block:
                parts.append(knowledge_block)

            term_block = self.build_term_mapping_block(
                knowledge.get('term_mapping', {})
            )
            if term_block:
                parts.append(term_block)

        return '\n\n'.join(parts)

    # ------------------------------------------------------------------
    # Блоки промпта — публичные (используются в тестах и контроллере)
    # ------------------------------------------------------------------

    def build_system_prompt(self, override=None):
        """Вернуть базовый системный промпт (для совместимости)."""
        return override if override else _SYSTEM_PROMPT_V2

    def build_safety_rules(self, mode='consult'):
        if mode == 'actions':
            return _ACTIONS_SAFETY_RULES
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
        lines = ['КОНТЕКСТ ЭКРАНА:']
        lines += [f'- {p}' for p in parts]
        return '\n'.join(lines)

    def build_knowledge_block(self, knowledge):
        """
        Принимает либо:
        - dict от KnowledgeProviderV2:
          {docs_snippets, tech_context, term_mapping}
        - list сниппетов от v1 KnowledgeProvider (обратная совместимость)
        """
        if not knowledge:
            return ''

        # Формат v1: список сниппетов
        if isinstance(knowledge, list):
            return self._build_knowledge_block_v1(knowledge)

        # Формат v2: словарь
        parts = []

        docs = knowledge.get('docs_snippets', '')
        if docs:
            parts.append('ДОКУМЕНТАЦИЯ:\n' + docs)

        tech = knowledge.get('tech_context')
        if tech:
            parts.append(
                '## Структура данных текущего модуля\n'
                'Техническая карта моделей и полей:\n\n'
                + tech
            )

        return '\n\n'.join(parts) if parts else ''

    def build_term_mapping_block(self, term_mapping):
        """Сформировать блок маппинга терминов для промпта."""
        if not term_mapping:
            return ''

        lines = ['МАППИНГ ТЕРМИНОВ Odoo 19 (EN → RU, используй эти названия):']

        buttons = term_mapping.get('buttons', {})
        if buttons:
            lines.append('Кнопки: ' + ', '.join(
                f'{en}→«{ru}»' for en, ru in list(buttons.items())[:20]
            ))

        menu_items = term_mapping.get('menu_items', {})
        if menu_items:
            lines.append('Меню: ' + ', '.join(
                f'{en}→«{ru}»' for en, ru in list(menu_items.items())[:20]
            ))

        removed = term_mapping.get('removed_in_v19', {})
        if removed:
            lines.append('Удалено в v19: ' + '; '.join(
                f'«{k}» — {v}' for k, v in removed.items()
            ))

        return '\n'.join(lines)

    def build_technical_context_block(self, technical_context):
        """Для обратной совместимости с контроллером v1."""
        if not technical_context:
            return ''
        return (
            '## Структура данных текущего модуля\n'
            'Ниже — техническая карта моделей, полей и связей. '
            'Используй её для точных ответов о полях, '
            'связях между моделями и доступных данных.\n\n'
            + technical_context
        )

    def _build_vision_prompt(self, message, context):
        """Специальный промпт для анализа скриншота (AIA-025)."""
        ctx = context or {}
        return (
            f"Пользователь прислал скриншот экрана Odoo 19.\n"
            f"Текущий контекст: модуль={ctx.get('module', '?')}, "
            f"модель={ctx.get('model', '?')}, "
            f"экран={ctx.get('view_type', '?')}.\n"
            f"Язык интерфейса: {ctx.get('lang', 'ru_RU')}.\n\n"
            f"Вопрос пользователя: {message}\n\n"
            f"Проанализируй скриншот и ответь, опираясь на то, "
            f"что РЕАЛЬНО видно на экране. Называй кнопки и меню "
            f"ТОЧНО так, как они отображены на скриншоте."
        )

    # ------------------------------------------------------------------
    # Внутренние
    # ------------------------------------------------------------------

    def _build_knowledge_block_v1(self, snippets):
        """Формат v1: список сниппетов с 'topic' и 'content'."""
        lines = ['Справочная документация по Odoo:']
        for snippet in snippets:
            topic = snippet.get('topic', '')
            content = snippet.get('content', '')
            if topic and content:
                lines.append(f'\n### {topic}\n{content}')
            elif content:
                lines.append(content)
        return '\n'.join(lines)
