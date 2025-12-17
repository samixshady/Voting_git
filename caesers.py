# Fixed lowercase substitution map
substitution_map = {
    'a': 'G', 'b': 'P', 'c': 'A', 'd': 'R', 'e': 'L', 'f': 'Y', 'g': 'H',
    'h': 'B', 'i': 'I', 'j': 'S', 'k': 'D', 'l': 'O', 'm': 'E', 'n': 'Z',
    'o': 'W', 'p': 'X', 'q': 'N', 'r': 'M', 's': 'J', 't': 'V', 'u': 'T',
    'v': 'F', 'w': 'M', 'x': 'C', 'y': 'K', 'z': 'U',
    '1': '4', '2': '7', '3': '1', '4': '8', '5': '9', '6': '2',
    '7': '3', '8': '0', '9': '5', '0': '6'
}

substitution_map.update({k.upper(): v.upper() for k, v in substitution_map.items()})
reverse_substitution_map = {v: k for k, v in substitution_map.items()}

def caesar_encrypt(text):
    result = []
    for char in text:
        if char in substitution_map:
            result.append(substitution_map[char])
        else:
            result.append(char)
    return ''.join(result)

def caesar_decrypt(text):
    result = []
    for char in text:
        if char in reverse_substitution_map:
            result.append(reverse_substitution_map[char])
        else:
            result.append(char)
    return ''.join(result)
