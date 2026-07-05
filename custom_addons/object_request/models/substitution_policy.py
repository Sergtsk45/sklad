import re

from odoo import api, models


DECISION_ALLOWED = "allowed_with_confirmation"
DECISION_BLOCKED = "blocked"
DECISION_UNKNOWN = "unknown_requires_review"


class ObjectRequestSubstitutionPolicy(models.AbstractModel):
    _name = "object.request.substitution.policy"
    _description = "Object request product substitution policy"

    @api.model
    def evaluate_texts(self, requested_text, candidate_text):
        requested = self._extract_features(requested_text)
        candidate = self._extract_features(candidate_text)
        reasons = []

        if not requested["family"] or not candidate["family"]:
            return self._decision(
                DECISION_UNKNOWN,
                "Не удалось надёжно определить семейство товара.",
                rule_applied=False,
            )

        if requested["family"] != candidate["family"]:
            return self._decision(
                DECISION_BLOCKED,
                "Семейство товара отличается: %s -> %s."
                % (requested["family"], candidate["family"]),
            )

        if requested["family"] != "flange":
            return self._decision(
                DECISION_UNKNOWN,
                "Для этого семейства нет формализованных правил замены.",
                rule_applied=False,
            )

        requested_diameter = requested["diameter"]
        candidate_diameter = candidate["diameter"]
        if not requested_diameter or not candidate_diameter:
            return self._decision(
                DECISION_UNKNOWN,
                "Не удалось надёжно определить DN/Ду для фланца.",
            )
        if requested_diameter != candidate_diameter:
            return self._decision(
                DECISION_BLOCKED,
                "Диаметр отличается: DN%s -> DN%s."
                % (requested_diameter, candidate_diameter),
            )
        reasons.append("Диаметр совпадает: DN%s." % requested_diameter)

        requested_pn = requested["pn"]
        candidate_pn = candidate["pn"]
        if requested_pn and candidate_pn:
            if candidate_pn < requested_pn:
                return self._decision(
                    DECISION_BLOCKED,
                    "Понижение давления запрещено: PN%s -> PN%s."
                    % (requested_pn, candidate_pn),
                )
            if candidate_pn > requested_pn:
                reasons.append(
                    "Допустимое повышение давления: PN%s -> PN%s."
                    % (requested_pn, candidate_pn)
                )
            else:
                reasons.append("Давление совпадает: PN%s." % requested_pn)
        else:
            reasons.append("Давление распознано не полностью.")

        for feature, label in [
            ("material", "материала"),
            ("gost", "ГОСТ"),
            ("execution", "исполнения"),
            ("connection", "типа соединения"),
        ]:
            requested_value = requested[feature]
            candidate_value = candidate[feature]
            if requested_value and candidate_value:
                if requested_value != candidate_value:
                    return self._decision(
                        DECISION_BLOCKED,
                        "Явный конфликт %s: %s -> %s."
                        % (label, requested_value, candidate_value),
                    )
                reasons.append("%s совпадает." % label.capitalize())
            elif requested_value or candidate_value:
                reasons.append(
                    "%s распознан не полностью, требуется подтверждение."
                    % label.capitalize()
                )

        return self._decision(DECISION_ALLOWED, " ".join(reasons))

    @api.model
    def _extract_features(self, text):
        normalized = self._normalize_text(text)
        return {
            "normalized": normalized,
            "family": self._extract_family(normalized),
            "diameter": self._extract_diameter(normalized),
            "pn": self._extract_pn(normalized),
            "material": self._extract_material(normalized),
            "gost": self._extract_gost(normalized),
            "execution": self._extract_execution(normalized),
            "connection": self._extract_connection(normalized),
        }

    @api.model
    def _normalize_text(self, text):
        value = (text or "").lower().replace("ё", "е")
        value = value.replace("\xa0", " ")
        value = re.sub(r"[,]+", ".", value)
        value = re.sub(r"\s+", " ", value)
        return value.strip()

    @api.model
    def _extract_family(self, text):
        if re.search(r"\bфлан(ец|ц[а-я]*)\b", text):
            return "flange"
        if re.search(r"\bкран\b", text):
            return "valve"
        if re.search(r"\bотвод\b", text):
            return "elbow"
        return False

    @api.model
    def _extract_diameter(self, text):
        patterns = [
            r"(?:ду|dn)\s*-?\s*(\d{1,3})\s*(?:мм)?\b",
            r"\b(\d{1,3})\s*мм\b",
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return int(match.group(1))
        return False

    @api.model
    def _extract_pn(self, text):
        pn_match = re.search(r"(?:pn|ру)\s*-?\s*(10|16)\b", text)
        if pn_match:
            return int(pn_match.group(1))
        mpa_match = re.search(r"\b1[.]([06])\s*мпа\b", text)
        if mpa_match:
            return 10 if mpa_match.group(1) == "0" else 16
        return False

    @api.model
    def _extract_material(self, text):
        if re.search(r"\b(латунь|латунный|лат)\b", text):
            return "brass"
        if re.search(r"\b(нерж|нержавеющ[а-я]*)\b", text):
            return "stainless"
        if re.search(r"\b(чугун|чугунный)\b", text):
            return "cast_iron"
        if re.search(r"\b(ст|сталь|стальной|стал)\b", text):
            return "steel"
        return False

    @api.model
    def _extract_gost(self, text):
        match = re.search(r"\bгост\s*([0-9][0-9.\-]*)", text)
        return match.group(1) if match else False

    @api.model
    def _extract_execution(self, text):
        match = re.search(r"\bисп(?:олнение)?\.?\s*-?\s*(\d+)\b", text)
        return match.group(1) if match else False

    @api.model
    def _extract_connection(self, text):
        connections = [
            ("flanged", r"\bфланцев[а-я]*\b"),
            ("threaded", r"\b(резьбов[а-я]*|муфтов[а-я]*)\b"),
            ("welded", r"\b(приварн[а-я]*|под\s*приварку)\b"),
        ]
        found = [
            value
            for value, pattern in connections
            if re.search(pattern, text)
        ]
        return found[0] if len(found) == 1 else False

    @api.model
    def _decision(
        self,
        decision,
        reason,
        rule_applied=True,
        requires_confirmation=True,
    ):
        return {
            "decision": decision,
            "reason": reason,
            "rule_applied": rule_applied,
            "requires_confirmation": requires_confirmation,
        }
