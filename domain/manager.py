

class Manager:

    def __init__(self):
        pass

    @staticmethod
    def emojize_name(country_name: str) -> str:
        """
        Return emoji to country
        """
        emoji_dict = {
            "Russia": "🇷🇺",
            "France": "🇫🇷",
            "England": "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
            "Championship": "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
            "Turkey": "🇹🇷",
            "Portugal": "🇵🇹",
            "Netherlands": "🇳🇱",
            "Italy": "🇮🇹",
            "UEFA_1": "🇪🇺",
            "UEFA_2": "🇪🇺",
            "Spain": "🇪🇸",
            "Germany": "🇩🇪"
        }
        return emoji_dict.get(country_name, default="🏁")

    @staticmethod
    def emojize_number(number: int) -> str:
        """
        Return emoji to number
        """
        emoji_dict = {
            1: ":one:",
            2: ":two:",
            3: ":three:",
            4: ":four:",
            5: ":five:",
            6: ":six:",
            7: ":seven:",
            8: ":eight:",
            9: ":nine:",
            10: "\U0001F51F"
        }
        return emoji_dict.get(number, default=":1234:")

    @staticmethod
    def emojize_coeff(self, coeff: float) -> str:
        """
        Return emoji to coeff
        """
        if coeff <= 1.5:
            return "🟩"
        elif coeff <= 2.0:
            return "🟨"
        elif coeff <= 3.0:
            return "🟧"
        else:
            return "🟥"
