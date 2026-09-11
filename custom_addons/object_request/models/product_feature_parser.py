import re

from odoo import api, models


class ObjectRequestProductFeatureParser(models.AbstractModel):
    _name = "object.request.product.feature.parser"
    _description = "Object request product technical feature parser"

    @api.model
    def parse_text(self, text):
        normalized = self.normalize_text(text)
        family = self.extract_family(normalized)
        diameter = self.extract_diameter(normalized)
        pressure = self.extract_pressure(normalized)
        material = self.extract_material(normalized)
        standard = self.extract_standard(normalized)
        connection = self.extract_connection(normalized)
        warnings = []
        if family in ("flange", "gasket", "reducer", "elbow", "valve"):
            if not diameter:
                warnings.append("Не найден DN/Ду.")
        return {
            "normalized": normalized,
            "product_family": family,
            "diameter_nominal": diameter,
            "pressure_nominal": pressure,
            "material": material,
            "standard": standard,
            "connection_type": connection,
            "warning": " ".join(warnings),
        }

    @api.model
    def normalize_text(self, text):
        value = (text or "").lower().replace("ё", "е")
        value = value.replace("\xa0", " ")
        value = re.sub(r"[,]+", ".", value)
        value = value.replace("×", "x")
        value = re.sub(r"(?<=\d)\s*х\s*(?=\d)", "x", value)
        value = re.sub(r"\s+", " ", value)
        return value.strip()

    @api.model
    def extract_family(self, text):
        if re.search(r"\bфлан(ец|ц[а-я]*)\b", text):
            return "flange"
        if re.search(r"\bпрокладк?[а-я]*\b", text):
            return "gasket"
        if "переход" in text or re.search(r"редукц[а-я]*", text):
            return "reducer"
        if re.search(r"\bотвод\b", text):
            return "elbow"
        if re.search(r"\b(кран|клапан|задвижк?[а-я]*)\b", text):
            return "valve"
        if re.search(r"\bтруб[аы]?\b", text):
            return "pipe"
        return False

    @api.model
    def extract_diameter(self, text):
        patterns = [
            r"(?:ду|dn)\s*-?\s*(\d{1,4})(?=\s*(?:мм\b|x|\b))",
            r"\b(\d{1,4})\s*мм\b",
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return int(match.group(1))
        return False

    @api.model
    def extract_pressure(self, text):
        pn_match = re.search(r"(?:pn|ру)\s*-?\s*(6|10|16|25|40)\b", text)
        if pn_match:
            return int(pn_match.group(1))
        mpa_match = re.search(r"\b([0-9]+(?:[.][0-9]+)?)\s*мпа\b", text)
        if mpa_match:
            value = float(mpa_match.group(1))
            return int(round(value * 10))
        return False

    @api.model
    def extract_material(self, text):
        if re.search(r"\b(латунь|латунный|лат)\b", text):
            return "brass"
        if re.search(r"\b(нерж|нержавеющ[а-я]*)\b", text):
            return "stainless"
        if re.search(r"\b(чугун|чугунный)\b", text):
            return "cast_iron"
        if re.search(r"\b(паронит|паронитов[а-я]*)\b", text):
            return "paronite"
        if re.search(r"\b(резин[а-я]*|epdm|nbr)\b", text):
            return "rubber"
        if re.search(r"\b(пвх|pvc)\b", text):
            return "pvc"
        if re.search(r"\b(ппр|полипропилен[а-я]*|pp)\b", text):
            return "polypropylene"
        if re.search(r"\b(ст|сталь|стальной|стал)\b", text):
            return "steel"
        return False

    @api.model
    def extract_standard(self, text):
        match = re.search(r"\bгост\s*([0-9][0-9.\-]*)", text)
        return match.group(1) if match else False

    @api.model
    def extract_connection(self, text):
        connections = [
            ("flanged", r"\b(фланцев[а-я]*|межфланцев[а-я]*)\b"),
            ("threaded", r"\b(резьбов[а-я]*|муфтов[а-я]*)\b"),
            ("welded", r"\b(приварн[а-я]*|под\s*приварку)\b"),
            ("socket", r"\bраструбн[а-я]*\b"),
        ]
        found = [
            value
            for value, pattern in connections
            if re.search(pattern, text)
        ]
        return found[0] if len(found) == 1 else False

    @api.model
    def feature_key(self, features):
        family = features.get("product_family")
        diameter = features.get("diameter_nominal")
        pressure = features.get("pressure_nominal")
        if not family or not diameter:
            return False
        return "%s|DN%s|PN%s" % (family, diameter, pressure or "-")
