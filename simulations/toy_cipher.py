"""Small classroom permutation with no real cipher compatibility."""
SBOX = (12, 5, 6, 11, 9, 0, 10, 13, 3, 14, 15, 8, 4, 7, 1, 2)


def encrypt(message, key, width, rounds):
    mask = (1 << width) - 1
    state = message
    for index in range(rounds):
        shift = index % width
        round_key = ((key << shift) | (key >> (width - shift))) & mask
        mixed = state ^ round_key ^ ((index * 0x9e37) & mask)
        state = sum(SBOX[(mixed >> bit) & 15] << bit for bit in range(0, width, 4))
        state = ((state << 3) | (state >> (width - 3))) & mask
    return state ^ key
