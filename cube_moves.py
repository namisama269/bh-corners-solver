import re

move_offsets = ("", "2", "'")
move_dirs = "uUlLfFrRbBdDMES"
move_rots = "xyz"
move_others = "34w2'"
move_valid_chars = move_dirs + move_rots + move_others

def is_valid_move(move):
    # Check all chars in move string are valid possible moves
    if len(move) == 0:
        return False
    if not all(ch in move_valid_chars for ch in move):
        return False

    # Wide turn with more than 2 layers
    if move[0].isdigit():
        # 2 or less layer turns do not require a number 
        if move[0] in "012":
            return False
        # If a number is present, must use "w" to signal a wide turn
        if len(move) < 3 or move[2] != 'w':
            return False
        move = move[1:]

    # Check that the directional indicator is valid
    if len(move) == 0 or move[0] not in move_dirs:
        return False
    move_dir = move[0]
    move = move[1:]

    # Remaining suffixes are "'", "2" possibly with w before
    if move_dir not in "ULFRBD":
        if len(move) != 0 and move[0] not in move_offsets:
            return False
        elif len(move) != 0:
            move = move[1:]
    else:
        if len(move) != 0 and move[0] == 'w':
            move = move[1:]

    # Remaining part should be a move offset
    return move in move_offsets

def is_commutator(comm):
    return ',' in comm or '/' in comm or '*' in comm or ':' in comm

def get_move_split_idx(move):
    idx = 0
    while idx < len(move) and move[idx] in move_valid_chars[:-2]:
        idx += 1
    return idx

def inverse_move(move):
    if len(move) > 2:
        move = move[:2]
    idx = get_move_split_idx(move)
    base = move[:idx]
    offset = move[idx:]
    return base + move_offsets[2-move_offsets.index(offset)]

def cancel_moves(move1, move2):
    idx1 = get_move_split_idx(move1)
    idx2 = get_move_split_idx(move2)

    base1 = move1[:idx1]
    base2 = move2[:idx2]
    if base1 != base2:
        return (False, move2)

    offset1 = move1[idx1:]
    offset2 = move2[idx2:]

    net_offset = (move_offsets.index(offset1) + move_offsets.index(offset2) + 2) % 4
    if net_offset == 0:
        return (True, None)
    else:
        return (True, base1 + move_offsets[net_offset-1])

def cancel_str(move_list):
    out_list = [move_list[0]]

    for i in range(1, len(move_list)):
        pop_prev, add_next = cancel_moves(move_list[i-1], move_list[i])
        if pop_prev:
            if len(out_list) > 0:
                out_list.pop()
        if add_next is not None:
            out_list.append(add_next)

    return out_list

def inverse_moves(move_str):
    move_str = move_str.split()
    return ' '.join(reversed([inverse_move(move) for move in move_str]))

def comm_to_moves(comm):
    if not is_commutator(comm):
        return comm

    # replace apostrophe
    comm = comm.replace("’", "'")

    comm = comm.replace('[', '').replace(']', '')
    comm = comm.replace('(', '').replace(')', '')
    comm = comm.replace('{', '').replace('}', '').strip()
    has_mul = False
    if '*' in comm:
        comm = comm[:comm.index('*')]
        has_mul = True
    has_setup = ':' in comm
    comm_list = [x.strip() for x in re.split(':|,|/', comm)]
    if len(comm_list) == 0:
        return ""

    move_str = ""
    if ',' in comm:
        move_str = comm_list[-2] + ' ' + comm_list[-1] + ' ' + inverse_moves(comm_list[-2]) + ' ' + inverse_moves(comm_list[-1])
    elif '/' in comm:
        move_str = comm_list[-2] + ' ' + comm_list[-1] + ' ' + comm_list[-2][0] + '2 ' + inverse_moves(comm_list[-1]) + ' ' + comm_list[-2]
    elif has_mul: 
        move_str = comm_list[-1] + ' ' + comm_list[-1]
    else: 
        move_str = comm_list[-1]
    if has_setup:
        move_str = comm_list[0] + ' ' + move_str + ' ' + inverse_moves(comm_list[0])

    # change 2' to 2 
    move_str = move_str.replace("2'", "2")
    move_list = move_str.split()

    out_list = cancel_str(move_list)
    for _ in range(len(out_list)):
        out_list = cancel_str(out_list)

    return ' '.join(out_list)

def inverse_comm(comm):
    if not is_commutator(comm):
        return comm

    add_sq_brackets = '[' in comm and ']' in comm
    # left and right brackets
    lbr = '[' if add_sq_brackets else ''
    rbr = ']' if add_sq_brackets else ''

    # replace apostrophe
    comm = comm.replace("’", "'")

    comm = comm.replace('[', '').replace(']', '')
    comm = comm.replace('(', '').replace(')', '')
    comm = comm.replace('{', '').replace('}', '').strip()
    has_mul = False
    if '*' in comm:
        comm = comm[:comm.index('*')]
        has_mul = True
    has_setup = ':' in comm
    comm_list = [x.strip() for x in re.split(':|,|/', comm)]
    if len(comm_list) == 0:
        return ""

    move_str = ""
    if ',' in comm:
        move_str = lbr + comm_list[-1] + ', ' + comm_list[-2] + rbr
    elif '/' in comm:
        move_str = '{' + f"{inverse_moves(comm_list[-2])}/{comm_list[-1]}" + '}'
    elif has_mul: 
        move_str = (f"({inverse_moves(comm_list[-1])}) * 2")
    else: 
        move_str = comm_list[-1]
    if has_setup:
        move_str = lbr + comm_list[0] + ': ' + move_str + rbr

    return move_str

def get_comm_parts(comm):
    if not is_commutator(comm):
        return comm

    parts = {
        'setup': "",
        'insertion': "",
        'interchange': "",
    }

    comm = comm.replace("’", "'")
    comm = comm.replace('[', '').replace(']', '')
    comm = comm.replace('(', '').replace(')', '')
    comm = comm.replace('{', '').replace('}', '').strip()

    has_setup = ':' in comm
    comm_list = [x.strip() for x in re.split(':|,|/', comm)]
    if len(comm_list) == 0:
        return parts

    parts['interchange'] = comm_list[-1] if len(comm_list[-1]) < len(comm_list[-2]) else comm_list[-2]
    parts['insertion'] = comm_list[-1] if len(comm_list[-1]) > len(comm_list[-2]) else comm_list[-2]
    if has_setup:
        setup = comm_list[0]

    return parts
    


if __name__ == "__main__":
    """
    comm = input()
    print(comm_to_moves(comm))
    print(inverse_comm(comm))
    """

    # multiple inputs
    comms = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        comms.append(line)

    print()
    print()
    print("==============================")
    for comm in comms:
        #print(comm_to_moves(comm))
        print(inverse_comm(comm))