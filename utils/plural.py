def plural(n: int, forms: list[str]) -> str:
    """
    Функция для склонения слов в зависимости от числа.

    :param n: число, для которого нужно склонять слово.
    :param forms: список форм слова в нужном порядке (например, ["яблоко", "яблока", "яблок"]).
    :return: строка со склоненным словом и числом.
    """
    if n % 10 == 1 and n % 100 != 11:
        return f"{n} {forms[0]}"
    elif n % 10 in [2, 3, 4] and n % 100 not in [12, 13, 14]:
        return f"{n} {forms[1]}"
    else:
        return f"{n} {forms[2]}"
