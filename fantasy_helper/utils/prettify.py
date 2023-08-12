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
            10: "\U0001F51F",
        }
        return emoji_dict.get(number, ":1234:")
    return (1 * (2 - len(str(number)))) * " " + str(number)


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
