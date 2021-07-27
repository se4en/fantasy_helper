

class Manager:

    def __init__(self):
        pass

    @staticmethod
    def emojize_league(league_name: str) -> str:
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
        return emoji_dict.get(league_name, "🏁")

    @staticmethod
    def emojize_number(number: int, more_10: bool = False) -> str:
        """
        Return emoji to number
        """
        if not more_10:
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
        else:
            emoji_dict = {
                0: ":zero::zero:",
                1: ":zero::one:",
                2: ":zero::two:",
                3: ":zero::three:",
                4: ":zero::four:",
                5: ":zero::five:",
                6: ":zero::six:",
                7: ":zero::seven:",
                8: ":zero::eight:",
                9: ":zero::nine:",
                10: ":one::zero:",
                11: ":one::one:",
                12: ":one::two:",
                13: ":one::three:",
                14: ":one::four:",
                15: ":one::five:",
                16: ":one::six:",
                17: ":one::seven:",
                18: ":one::eight:",
                19: ":one::nine:",
                20: ":two::zero:"
            }

        return emoji_dict.get(number, ":1234:")

    @staticmethod
    def emojize_coeff(coeff: float) -> str:
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

    @staticmethod
    def translate_league(league_name: str) -> str:
        translate_dict = {
            'Russia': 'РПЛ',
            'England': 'АПЛ',
            'France': 'Лига 1',
            'Germany': 'Бундеслига',
            'Spain': 'Ла Лига',
            'Netherlands': 'Эредевизи',
            'Championship': 'Чемпионшип',
            'Turkey': 'Суперлига',
            'Italy': 'Серия А',
            'Portugal': 'Премьер-лига',
            'UEFA_1': 'Лига Чемпионов',
            'UEFA_2': 'Лига Европы'
        }
        return translate_dict.get(league_name, '')
