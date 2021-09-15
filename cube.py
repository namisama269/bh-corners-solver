
single_moves = ["U", "L", "F", "R", "B", "D"]
move_dirs = {
    "": 1,
    "'": 3,
    "2": 2,
}

opposite_moves = {
    "U": "D", 
    "L": "R", 
    "F": "B", 
    "R": "L", 
    "B": "F", 
    "D": "U",
}

opposite_dirs = {
    "": "'",
    "'": "",
    "2": "2"   
}

pieces = [
    ['UFR','RUF','FUR'], ['UFL','FUL','LUF'], ['UBL','LUB','BUL'], ['UBR','BUR','RUB'],
    ['DFR','FDR','RDF'], ['DBR','RDB','BDR'], ['DBL','BDL','LDB'], ['DFL','LDF','FDL'], 
]

def get_piece_idx(target):
    i = 0
    while i < len(pieces):
        if target in pieces[i]:
            break
        i += 1
    return i

def target_to_idx(target):
    return {
        'UBL': 0, 'UBR': 1, 'UFR': 2, 'UFL': 3,
        'LUB': 4, 'LUF': 5, 'LDF': 6, 'LDB': 7,
        'FUL': 8, 'FUR': 9, 'FDR': 10, 'FDL': 11,
        'RUF': 12, 'RUB': 13, 'RDB': 14, 'RDF': 15,
        'BUR': 16, 'BUL': 17, 'BDL': 18, 'BDR': 19,
        'DFL': 20, 'DFR': 21, 'DBR': 22, 'DBL': 23,
    }[target]

def idx_to_target(idx):
    return [
        'UBL', 'UBR', 'UFR', 'UFL',
        'LUB', 'LUF', 'LDF', 'LDB',
        'FUL', 'FUR', 'FDR', 'FDL',
        'RUF', 'RUB', 'RDB', 'RDF',
        'BUR', 'BUL', 'BDL', 'BDR',
        'DFL', 'DFR', 'DBR', 'DBL',
    ][idx]

def replace_at_idx(string, idx, new_str):
    return string[:idx] + new_str + string[idx+1:]

def do_move(target, move):
    md = "" if len(move) == 1 else move[1:]
    move = move[0]

    # Move does not affect the target
    if move not in target:
        return target

    # Target is on the same face as the move 
    if target[0] == move[0]:
        new_idx = target_to_idx(target) + move_dirs[md]
        if new_idx >= (single_moves.index(move) * 4 + 4):
            new_idx -= 4
        return idx_to_target(new_idx)

    # Case-specific side targets
    side_targets = {
        "U": ['LUB','BUL','BUR','RUB','RUF','FUR','FUL','LUF'],
        "L": ['UBL','BUL','FUL','UFL','DFL','FDL','BDL','DBL'],
        "F": ['UFL','LUF','RUF','UFR','DFR','RDF','LDF','DFL'],
        "R": ['UBR','BUR','BDR','DBR','DFR','FDR','FUR','UFR'],
        "B": ['UBL','LUB','LDB','DBL','DBR','RDB','RUB','UBR'],
        "D": ['LDB','BDL','FDL','LDF','RDF','FDR','BDR','RDB'],
    }

    new_idx = (side_targets[move].index(target) + 2 * move_dirs[md]) % 8
    return side_targets[move][new_idx]

def do_moves(target, moves):
    for move in moves.split():
        target = do_move(target, move)
    return target

    
if __name__ == "__main__":
    target = input("Enter target: ")
    moves = input("Enter moves: ")
    print(do_moves(target, moves))
