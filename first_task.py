"""1.Напишите программу, которая выводит n первых элементов последовательности 122333444455555… 
(число повторяется столько раз, чему оно равно)."""


def print_n_elements(n: int) -> None:
    """Выводит n первых элементов последовательности 122333444455555…"""
    current = 1
    number = 0
    quantity = 0
    if n <= 0:
        return None
    while quantity < n:
        number += 1
        print(current, end='')
        if number >= current:
            current += 1
            number = 0
        quantity += 1


if __name__ == '__main__':
    n = int(input('Введите число элементов последовательности: '))
    print_n_elements(n)
