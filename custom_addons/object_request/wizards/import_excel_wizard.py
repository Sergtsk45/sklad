import base64
import io
import re

from odoo import models, fields
from odoo.exceptions import UserError


class ObjectRequestImportPreview(models.TransientModel):
    _name = "object.request.import.preview"
    _description = "Предпросмотр строк импорта Excel"
    _order = "sequence, id"

    wizard_id = fields.Many2one(
        "object.request.import.wizard",
        string="Wizard",
        required=True,
        ondelete="cascade",
    )
    sequence = fields.Integer(string="№ п/п")
    source_row_no = fields.Integer(string="Строка Excel")
    supplier_article = fields.Char(string="Артикул")
    name_raw = fields.Char(string="Наименование")
    uom_raw = fields.Char(string="Ед. изм.")
    qty = fields.Float(string="Количество")
    price = fields.Float(string="Цена")
    comment = fields.Char(string="Комментарий")
    supplier_raw = fields.Char(string="Поставщик")
    matched_product_id = fields.Many2one(
        "product.product",
        string="Товар (сопоставлен)",
        readonly=True,
    )
    matched_vendor_id = fields.Many2one(
        "res.partner",
        string="Поставщик (сопоставлен)",
        readonly=True,
    )
    candidate_product_ids = fields.Many2many(
        "product.product",
        string="Кандидаты",
        readonly=True,
    )
    match_status = fields.Selection(
        [("matched", "Сопоставлен"), ("unmatched", "Не сопоставлен")],
        string="Статус",
        readonly=True,
    )
    matching_required = fields.Boolean(
        string="Требует сопоставления",
        readonly=True,
    )
    manual_vendor_required = fields.Boolean(
        string="Требует выбора поставщика",
        readonly=True,
    )
    has_error = fields.Boolean(string="Ошибка", readonly=True)
    error_message = fields.Char(string="Описание ошибки", readonly=True)


class ObjectRequestImportWizard(models.TransientModel):
    _name = "object.request.import.wizard"
    _description = "Wizard импорта Excel — Требование на комплектацию"

    # --- Файл ---
    file = fields.Binary(string="Excel файл", required=True)
    file_name = fields.Char(string="Имя файла")

    # --- Параметры документа ---
    project_id = fields.Many2one(
        "object.request.project",
        string="Объект",
        required=True,
    )
    foreman_user_id = fields.Many2one(
        "res.users",
        string="Прораб",
        required=True,
        default=lambda self: self.env.user,
    )
    need_date = fields.Date(string="Дата потребности", required=True)
    priority = fields.Selection(
        [
            ("0", "Низкий"),
            ("1", "Обычный"),
            ("2", "Высокий"),
            ("3", "Критический"),
        ],
        string="Приоритет",
        default="1",
        required=True,
    )
    comment = fields.Text(string="Комментарий")
    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company,
        readonly=True,
    )

    # --- Результаты парсинга ---
    preview_line_ids = fields.One2many(
        "object.request.import.preview",
        "wizard_id",
        string="Предпросмотр строк",
    )
    line_preview_count = fields.Integer(
        string="Строк распознано",
        readonly=True,
    )
    problem_line_count = fields.Integer(
        string="Строк с ошибками",
        readonly=True,
    )
    validation_state = fields.Selection(
        [
            ("not_checked", "Не проверено"),
            ("valid", "Файл корректен"),
            ("invalid", "Ошибка файла"),
        ],
        string="Статус проверки",
        default="not_checked",
        readonly=True,
    )
    validation_messages = fields.Text(
        string="Сообщения проверки",
        readonly=True,
    )

    _COLUMN_SYNONYMS = {
        "supplier_article": ("артикул", "арт", "арт.", "обозначение"),
        "name_raw": ("наименование", "наим", "наим.", "наименование товара"),
        "uom_raw": (
            "ед",
            "ед.",
            "ед изм",
            "ед. изм.",
            "единица измерения",
        ),
        "qty": ("кол-во", "кол", "кол.", "количество"),
        "price": ("цена", "цена за ед", "цена за единицу"),
        "comment": (
            "ком",
            "ком.",
            "комм",
            "комм.",
            "комментарий",
            "примечание",
        ),
        "supplier_raw": ("пост", "пост.", "поставщик"),
    }

    _REQUIRED_COLUMNS = ("name_raw", "qty")
    _COLUMN_LABELS = {
        "supplier_article": "артикул / обозначение",
        "name_raw": "наименование",
        "uom_raw": "единица измерения",
        "qty": "количество",
        "price": "цена",
        "comment": "комментарий",
        "supplier_raw": "поставщик",
    }

    # --- Приватные методы ---

    def _parse_excel(self):
        """Читает Excel-файл. Возвращает (rows, None) или (None, error)."""
        try:
            import openpyxl  # noqa: PLC0415
        except ImportError:
            raise UserError(
                "Не установлена библиотека openpyxl. "
                "Выполните внутри контейнера: pip install openpyxl"
            )

        try:
            file_data = base64.b64decode(self.file)
            workbook = openpyxl.load_workbook(
                io.BytesIO(file_data),
                read_only=True,
                data_only=True,
            )
        except Exception as e:
            return None, f"Не удалось открыть файл: {e}"

        sheet = workbook.active
        rows = list(sheet.iter_rows(values_only=True))
        workbook.close()

        if not rows:
            return None, "Файл пустой."

        return rows, None

    @classmethod
    def _normalize_header(cls, value):
        """Нормализует заголовок Excel для устойчивого сопоставления."""
        header = cls._to_str(value).lower().replace("\xa0", " ")
        header = re.sub(r"\s+", " ", header).strip()
        return header.replace(".", "")

    @classmethod
    def _column_synonyms_normalized(cls):
        return {
            field_name: {
                cls._normalize_header(synonym)
                for synonym in synonyms
            }
            for field_name, synonyms in cls._COLUMN_SYNONYMS.items()
        }

    def _map_columns(self, header_row):
        """Возвращает mapping полей импорта на индексы колонок Excel."""
        synonyms = self._column_synonyms_normalized()
        mapping = {}
        for idx, header in enumerate(header_row):
            normalized = self._normalize_header(header)
            if not normalized:
                continue
            for field_name, variants in synonyms.items():
                if field_name not in mapping and normalized in variants:
                    mapping[field_name] = idx
                    break
        return mapping

    def _get_mapped_header(self, header_row, mapping, field_name):
        idx = mapping.get(field_name)
        if idx is None or idx >= len(header_row):
            return ""
        return self._normalize_header(header_row[idx])

    def _describe_import_format(self, header_row, mapping):
        name_header = self._get_mapped_header(header_row, mapping, "name_raw")
        article_header = self._get_mapped_header(
            header_row,
            mapping,
            "supplier_article",
        )
        uom_header = self._get_mapped_header(header_row, mapping, "uom_raw")
        qty_header = self._get_mapped_header(header_row, mapping, "qty")

        if (
            name_header == "наименование"
            and article_header == "обозначение"
            and uom_header == "единица измерения"
            and qty_header == "количество"
        ):
            return (
                "Распознан формат: спецификация УУТЭ "
                "(Обозначение используется как артикул поставщика)"
            )
        if (
            article_header == "артикул"
            and name_header == "наименование"
            and uom_header in {"ед", "ед изм"}
            and qty_header == "кол-во"
        ):
            return "Распознан формат: стандартный импорт wizard"
        return "Распознан формат: гибкий импорт по заголовкам"

    def _format_supported_headers(self, field_names):
        lines = []
        for field_name in field_names:
            label = self._COLUMN_LABELS[field_name]
            variants = ", ".join(self._COLUMN_SYNONYMS[field_name])
            lines.append(f"- {label}: {variants}")
        return "\n".join(lines)

    def _format_found_headers(self, header_row):
        headers = [
            self._to_str(header)
            for header in header_row
            if self._to_str(header)
        ]
        return ", ".join(headers) if headers else "нет заголовков"

    def _validate_columns(self, header_row, mapping):
        """Проверяет структуру заголовка. Возвращает список ошибок."""
        errors = []
        missing_required = [
            field_name
            for field_name in self._REQUIRED_COLUMNS
            if field_name not in mapping
        ]
        if missing_required:
            labels = [
                self._COLUMN_LABELS[field_name]
                for field_name in missing_required
            ]
            errors.append(
                "Не найдены обязательные колонки: %s.\n"
                "Найденные заголовки: %s.\n"
                "Поддерживаемые варианты заголовков:\n%s"
                % (
                    ", ".join(labels),
                    self._format_found_headers(header_row),
                    self._format_supported_headers(missing_required),
                )
            )
        return errors

    @staticmethod
    def _to_str(val):
        return str(val).strip() if val is not None else ""

    @staticmethod
    def _to_float(val):
        if val is None:
            return 0.0
        try:
            return float(val)
        except (ValueError, TypeError):
            return 0.0

    @classmethod
    def _get_mapped_cell(cls, row, mapping, field_name, default=""):
        idx = mapping.get(field_name)
        if idx is None or idx >= len(row):
            return default
        return row[idx]

    def _build_preview_vals(self, rows, column_mapping):
        """Парсит строки Excel с автосопоставлением.

        Returns:
            tuple: (preview_vals list, problem_count int)
        """
        parser = self.env["object.request.excel.parser"].sudo()
        preview_vals = []
        problem_count = 0
        seq = 0

        for row_idx, row in enumerate(rows[1:], start=2):
            if not any(cell for cell in row):
                continue

            seq += 1
            supplier_article = parser.normalize_str(
                self._to_str(
                    self._get_mapped_cell(
                        row,
                        column_mapping,
                        "supplier_article",
                    )
                )
            )
            name_raw = self._to_str(
                self._get_mapped_cell(row, column_mapping, "name_raw")
            )
            uom_raw = parser.normalize_uom(
                self._to_str(
                    self._get_mapped_cell(row, column_mapping, "uom_raw")
                )
            )
            qty = self._to_float(
                self._get_mapped_cell(row, column_mapping, "qty", 0.0)
            )
            price = self._to_float(
                self._get_mapped_cell(row, column_mapping, "price", 0.0)
            )
            comment = self._to_str(
                self._get_mapped_cell(row, column_mapping, "comment")
            )
            supplier_raw = parser.normalize_str(
                self._to_str(
                    self._get_mapped_cell(row, column_mapping, "supplier_raw")
                )
            )

            has_error, error_msg = False, ""
            if not name_raw:
                has_error, error_msg = True, "Пустое наименование"
            elif qty <= 0:
                has_error, error_msg = True, "Количество не указано или 0"

            if has_error:
                problem_count += 1

            match = parser.match_row(supplier_article, name_raw, supplier_raw)
            product = match["product"]
            vendor = match["vendor"]
            candidates = match.get("candidate_products")

            preview_vals.append(
                {
                    "wizard_id": self.id,
                    "sequence": seq,
                    "source_row_no": row_idx,
                    "supplier_article": supplier_article,
                    "name_raw": name_raw,
                    "uom_raw": uom_raw,
                    "qty": qty,
                    "price": price,
                    "comment": comment,
                    "supplier_raw": supplier_raw,
                    "matched_product_id": product.id if product else False,
                    "matched_vendor_id": vendor.id if vendor else False,
                    "candidate_product_ids": [
                        (6, 0, candidates.ids)
                    ] if candidates else False,
                    "match_status": "matched" if product else "unmatched",
                    "matching_required": match["matching_required"],
                    "manual_vendor_required": match["manual_vendor_required"],
                    "has_error": has_error,
                    "error_message": error_msg,
                }
            )

        return preview_vals, problem_count

    # --- Публичные методы ---

    def action_validate(self):
        """Загружает файл, валидирует структуру, строит предпросмотр."""
        self.ensure_one()
        self.preview_line_ids.unlink()

        rows, parse_error = self._parse_excel()
        if parse_error:
            self.write(
                {
                    "validation_state": "invalid",
                    "validation_messages": parse_error,
                    "line_preview_count": 0,
                    "problem_line_count": 0,
                }
            )
            return self._reopen()

        if len(rows) < 2:
            self.write(
                {
                    "validation_state": "invalid",
                    "validation_messages": (
                        "Файл не содержит строк данных "
                        "(только заголовок или пустой)."
                    ),
                    "line_preview_count": 0,
                    "problem_line_count": 0,
                }
            )
            return self._reopen()

        column_mapping = self._map_columns(rows[0])
        col_errors = self._validate_columns(rows[0], column_mapping)
        if col_errors:
            self.write(
                {
                    "validation_state": "invalid",
                    "validation_messages": "\n".join(col_errors),
                    "line_preview_count": 0,
                    "problem_line_count": 0,
                }
            )
            return self._reopen()

        preview_vals, problem_count = self._build_preview_vals(
            rows,
            column_mapping,
        )

        if not preview_vals:
            self.write(
                {
                    "validation_state": "invalid",
                    "validation_messages": "Файл не содержит строк с данными.",
                    "line_preview_count": 0,
                    "problem_line_count": 0,
                }
            )
            return self._reopen()

        self.env["object.request.import.preview"].create(preview_vals)

        total = len(preview_vals)
        matched = sum(1 for v in preview_vals if not v["matching_required"])
        unmatched = total - matched
        messages = [
            self._describe_import_format(rows[0], column_mapping),
            f"Распознано строк: {total}",
            f"Сопоставлено товаров: {matched}",
        ]
        if unmatched:
            messages.append(f"Требуют сопоставления: {unmatched}")
        if "uom_raw" not in column_mapping:
            messages.append(
                "Предупреждение: колонка единицы измерения не распознана; "
                "строки будут импортированы без ед. изм. из файла."
            )
        if problem_count:
            messages.append(
                f"Строк с ошибками (предупреждение): {problem_count}"
            )

        self.write(
            {
                "validation_state": "valid",
                "validation_messages": "\n".join(messages),
                "line_preview_count": total,
                "problem_line_count": problem_count,
            }
        )
        return self._reopen()

    def action_import(self):
        """Создаёт документ object.request и строки из preview (OBR-007)."""
        self.ensure_one()
        if self.validation_state != "valid":
            raise UserError(
                "Сначала загрузите и проверьте файл "
                "(кнопка «Загрузить и проверить»)."
            )
        if not self.preview_line_ids:
            raise UserError("Нет строк для импорта. Загрузите файл повторно.")

        request = self.env["object.request"].create(
            {
                "project_id": self.project_id.id,
                "foreman_user_id": self.foreman_user_id.id,
                "need_date": self.need_date,
                "priority": self.priority,
                "comment": self.comment,
                "source_file_name": self.file_name or "",
                "imported_at": fields.Datetime.now(),
                "imported_by_user_id": self.env.uid,
            }
        )

        line_vals = []
        for preview in self.preview_line_ids:
            uom_id = False
            product = preview.matched_product_id
            if product and product.uom_id:
                uom_id = product.uom_id.id
            line_vals.append(
                {
                    "request_id": request.id,
                    "sequence": preview.sequence,
                    "source_row_no": preview.source_row_no,
                    "supplier_article": preview.supplier_article,
                    "name_raw": preview.name_raw,
                    "uom_raw": preview.uom_raw,
                    "qty_requested": preview.qty,
                    "price_raw": preview.price,
                    "comment": preview.comment,
                    "supplier_raw": preview.supplier_raw,
                    "product_id": preview.matched_product_id.id or False,
                    "uom_id": uom_id,
                    "preferred_vendor_id": preview.matched_vendor_id.id
                    or False,
                    "matching_required": preview.matching_required,
                    "manual_vendor_required": preview.manual_vendor_required,
                    "matching_note": (
                        "import auto match"
                        if preview.matched_product_id
                        and not preview.matching_required
                        else False
                    ),
                    "matching_source": (
                        "import_auto"
                        if preview.matched_product_id
                        and not preview.matching_required
                        else "unknown"
                    ),
                }
            )

        if line_vals:
            self.env["object.request.line"].create(line_vals)

        return {
            "type": "ir.actions.act_window",
            "res_model": "object.request",
            "res_id": request.id,
            "view_mode": "form",
            "target": "current",
        }

    def _reopen(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }
