from cube import pieces, get_piece_idx
from solver import classify_comm, get_bh_comms
from cube_moves import comm_to_moves, inverse_comm

def get_cycles(comm_notation = True):
    bf, t1, t2 = input("Enter cycle: ").split()
    print()
    solns = get_bh_comms(bf, t1, t2)
    if comm_notation:
        for soln in solns:
            print(soln)
    else:
        soln_moves = list(set([comm_to_moves(soln) for soln in solns]))
        for soln in soln_moves:
            print(soln)

def print_buffer_cycles(bf, show_type = False):
    for i in range(len(pieces)):
            for j in range(len(pieces)):
                if i == j:
                    continue
                for k in range(len(pieces[i])):
                    for l in range(len(pieces[j])):
                        p1 = pieces[i][k]
                        p2 = pieces[j][l]
                        if (p1 in pieces[get_piece_idx(bf)] or p2 in pieces[get_piece_idx(bf)]):
                            continue
                        if i > j:
                            soln = inverse_comm(get_bh_comms(bf, p2, p1)[0])
                        else:
                            soln = get_bh_comms(bf, p1, p2)[0]

                        commtype = classify_comm(bf, p1, p2)
                        if show_type:
                            print(f"{bf} {p1} {p2}: {soln:<40}" + f"    ({commtype})") 
                        else:
                            print(f"{bf} {p1} {p2}: {soln}")
    

if __name__ == "__main__":
    #get_cycles(False)
    buffer = input("Enter buffer: ")
    print()
    print_buffer_cycles(buffer, show_type=True)