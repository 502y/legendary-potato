threat_level_to_number = {
    '高': 0,
    '中': 1,
    '低': 2,
    '警告': 3,
    '提示': 4,
}

number_to_threat_level = {v: k for k, v in threat_level_to_number.items()}


class ThreatModel:
    @staticmethod
    def text_to_number(text):
        return threat_level_to_number.get(text, None)

    @staticmethod
    def number_to_text(number):
        return number_to_threat_level.get(number, None)
