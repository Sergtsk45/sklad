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
        parser = self.env["object.request.product.feature.parser"]
        parsed = parser.parse_text(text)
        return {
            "normalized": parsed["normalized"],
            "family": parsed["product_family"],
            "diameter": parsed["diameter_nominal"],
            "pn": parsed["pressure_nominal"],
            "material": parsed["material"],
            "gost": parsed["standard"],
            "execution": self._extract_execution(parsed["normalized"]),
            "connection": parsed["connection_type"],
        }

    @api.model
    def _extract_execution(self, text):
        import re

        match = re.search(r"\bисп(?:олнение)?\.?\s*-?\s*(\d+)\b", text)
        return match.group(1) if match else False

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
