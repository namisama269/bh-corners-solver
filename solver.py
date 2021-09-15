
import re
from cube import do_moves, single_moves, opposite_moves, opposite_dirs, pieces, get_piece_idx
from cube_moves import comm_to_moves, inverse_comm, get_comm_parts, inverse_move, inverse_moves

def get_interchange(t1, t2):
    for move in single_moves:
        for md in ["", "'", "2"]:
            if do_moves(t1, move+md) == t2:
                return move+md
    return None

def get_piece_dist(t1, t2):
    unique_ltrs = set([t1[0], t1[1], t1[2], t2[0], t2[1], t2[2]])
    return len(unique_ltrs) - 3

def get_common_face(t1, t2, t3):
    # Return the face that all 3 targets are on, None if does not exist
    for move in single_moves:
        if move in t1 and move in t2 and move in t3:
            return move
    return None

def is_opp(t1, t2):
    return get_piece_dist(t1, t2) > 1

def is_adj(t1, t2):
    return get_piece_dist(t1, t2) <= 1

def is_inter(t1, t2):
    return get_interchange(t1, t2) is not None

def is_opi(t1, t2):
    # OpI = opposite and interchangeable
    return is_inter(t1, t2) and is_opp(t1, t2)

def is_ani(t1, t2):
    # AnI = adjacent not interchangeable
    return not is_inter(t1, t2)

def is_oni(t1, t2):
    # AnI = adjacent not interchangeable
    return not is_inter(t1, t2) and is_opp(t1, t2)

def is_coplanar(t1, t2, t3):
    return get_common_face(t1, t2, t3) is not None

def has_column(t1, t2, t3):
    dists = []
    pairs = [(t1, t2), (t1, t3), (t2, t3)]
    for pair in pairs:
        p1, p2 = pair
        dist = get_piece_dist(p1, p2)
        if dist == 1 and not is_inter(p1, p2):
            dists.append(dist)
        if dist == 2 and is_inter(p1, p2):
            dists.append(dist)
        if dist == 3:
            dists.append(dist)
    return 1 in dists and 2 in dists and 3 in dists

def is_in_layer(target, layer):
    return layer in target

def classify_comm(bf, t1, t2):
    """
    Basic classification of comms without searching for insertions, only filters out 
    Per Special, Cyclic Shift, Orthogonal, Columns comms.
    """
    # Per Special --> all 3 targets OpI
    if is_opi(bf, t1) and is_opi(t1, t2) and is_opi(t2, bf):
        return "Per Special"
    # Cyclic Shift --> all 3 targets coplanar and AnI
    if (not (is_inter(bf, t1) or is_inter(t1, t2) or is_inter(t2, bf))) and \
    is_coplanar(bf, t1 ,t2):
        return "Cyclic Shift"
    # Orthogonal --> all 3 targets non-interchangeable, 2 targets opposite to buffer
    if (not (is_inter(bf, t1) or is_inter(t1, t2) or is_inter(t2, bf))) and \
    is_oni(bf, t1) and is_oni(bf, t2) and is_oni(t1, t2):
        return "Orthogonal"
    # Columns --> 2 targets OpI, 3rd not interchangeable to first 2
    if has_column(bf, t1, t2):
        return "Columns"
    # Else, is Pure/A9
    return "Pure/A9"

def classify_comm(bf, t1, t2):
    # Per Special --> all 3 targets OpI
    if is_opi(bf, t1) and is_opi(t1, t2) and is_opi(t2, bf):
        return "Per Special"
    # Cyclic Shift --> all 3 targets coplanar and AnI
    if (not (is_inter(bf, t1) or is_inter(t1, t2) or is_inter(t2, bf))) and \
    is_coplanar(bf, t1 ,t2):
        return "Cyclic Shift"
    # Orthogonal --> all 3 targets non-interchangeable, 2 targets opposite to buffer
    if (not (is_inter(bf, t1) or is_inter(t1, t2) or is_inter(t2, bf))) and \
    is_oni(bf, t1) and is_oni(bf, t2) and is_oni(t1, t2):
        return "Orthogonal"
    # Columns --> 2 targets OpI, 3rd not interchangeable to first 2
    if has_column(bf, t1, t2):
        return "Columns"
    # Search for a pure comm to determine whether Pure or A9
    pure_solns = search_pure_comm(bf, t1, t2)
    return "A9" if len(pure_solns) == 0 else "Pure"

def search_insertion(t1, t2, inter, restricted_inserts = []):
    """
    Search for an insertion that preserves the interchange layer. Either 1 insertion
    exists or no insertion can be found.
    """
    side_moves = single_moves.copy()
    mid_move = opposite_moves[inter[0]]
    side_moves.remove(inter[0])
    side_moves.remove(mid_move)
    for restricted_insert in restricted_inserts:
        if restricted_insert in side_moves:
            side_moves.remove(restricted_inserts)

    for sm in side_moves:
        for sd in ["", "'"]:
            for md in ["", "'", "2"]:
                insertion = f"{sm}{sd} {mid_move}{md} {sm}{opposite_dirs[sd]}"
                if do_moves(t1, insertion) == t2:
                    return insertion

    # No insertion can be found
    return None

def search_opt_1move_setup(bf, t1, t2):
    is_a9_optimal = False
    solns = []
    for st1 in single_moves:
        for sd1 in ["", "'", "2"]:
            nbf, nt1, nt2 = do_moves(bf, st1+sd1), do_moves(t1, st1+sd1), do_moves(t2, st1+sd1)
            pure_solns = search_pure_comm(nbf, nt1, nt2)
            for soln in pure_solns:
                # Found A9, remove all 10 move solns as they are no longer optimal
                soln = f"[{st1+sd1}: {soln}]"
                parts = get_comm_parts(soln)
                if st1 == parts['insertion'][0] or st1 == parts['interchange'][0]:
                    if not is_a9_optimal:
                        solns.clear()
                        is_a9_optimal = True
                    solns.append(soln)
                else:
                    if not is_a9_optimal:
                        solns.append(soln)
    return solns

def search_1move_cyclic_shift(bf, t1, t2):
    # Search for a quarter turn into a cyclic shift
    solns = []
    for st1 in single_moves:
        for sd1 in ["", "'"]:
            nbf, nt1, nt2 = do_moves(bf, st1+sd1), do_moves(t1, st1+sd1), do_moves(t2, st1+sd1)
            if classify_comm(nbf, nt1, nt2) != "Cyclic Shift":
                continue
            pure_solns = search_cyclic_shift(nbf, nt1, nt2)
            for soln in pure_solns:
                soln = f"[{st1+sd1}: {soln}]"
                solns.append(soln)
    return solns

def search_opt_2move_setup(bf, t1, t2):
    is_11_optimal = False
    solns = []
    for st1 in single_moves:
        for sd1 in ["", "'", "2"]:
            for st2 in single_moves:
                for sd2 in ["", "'", "2"]:
                    nbf, nt1, nt2 = do_moves(bf, st1+sd1+' '+st2+sd2), do_moves(t1, st1+sd1+' '+st2+sd2), do_moves(t2, st1+sd1+' '+st2+sd2)
                    pure_solns = search_pure_comm(nbf, nt1, nt2)
                    for soln in pure_solns:
                        # Found 11 move soln, remove all 12 move solns as they are no longer optimal
                        soln = f"[{st1+sd1+' '+st2+sd2}: {soln}]"
                        parts = get_comm_parts(soln)
                        if st2 == parts['insertion'][0] or st2 == parts['interchange'][0]:
                            if not is_11_optimal:
                                solns.clear()
                                is_11_optimal = True
                            solns.append(soln)
                        else:
                            if not is_11_optimal:
                                solns.append(soln)
    return solns

def search_pure_comm(bf, t1, t2, restricted_inserts = []):
    solns = []

    inters = [(bf,t1), (t1,bf), (t1,t2), (t2,t1), (t2,bf), (bf,t2)]
    inserts = [(t2,t1), (t2,bf), (bf,t2), (bf,t1), (t1,bf), (t1,t2)]
    for i in range(6):
        inter = get_interchange(inters[i][0], inters[i][1])
        if inter is not None: 
            insertion = search_insertion(inserts[i][0], inserts[i][1], inter, restricted_inserts)
            if insertion is not None:
                comm = f"[{insertion}, {inter}]"
                if do_moves(bf, comm_to_moves(comm)) == t1:
                    solns.append(comm)
                else:
                    solns.append(inverse_comm(comm))
                #print(solns)
    
    return solns

def search_cyclic_shift(bf, t1, t2):
    # Find the common face
    face = get_common_face(bf, t1, t2)

    # Find the middle piece
    if get_piece_dist(bf, t1) == 1 and get_piece_dist(bf, t2) == 1:
        middle = bf
    if get_piece_dist(t1, bf) == 1 and get_piece_dist(t1, t2) == 1:
        middle = t1
    if get_piece_dist(t2, bf) == 1 and get_piece_dist(t2, t1) == 1:
        middle = t2

    # Convert the cycle so that the middle is the start
    if middle == t1:
        bf, t1, t2 = t1, t2, bf
    if middle == t2:
        bf, t1, t2 = t2, bf, t1

    # Loading spot is double face turn away from middle
    loader = do_moves(middle, face + '2')

    # Find the 2 inverse setups (what move brings loader to t1 and t2)
    s1 = get_interchange(loader, t1)
    s2 = get_interchange(loader, t2)

    soln = f"({inverse_moves(s2)} {inverse_move(s1)} {face}2 {s1} {s2}) "
    soln += f"({inverse_moves(s1)} {inverse_move(s2)} {face}2 {s2} {s1})"
    return [soln]

def get_perspecial_setups(target, layer, moveset):
    setups = []
    for move in moveset:
        for md in ["", "'"]:
            new_target = do_moves(target, move+md)
            if is_in_layer(new_target, layer):
                setups.append(move+md)
    return setups

def mirror(move):
    md = "" if len(move) == 1 else move[1:]
    move = move[0]
    return opposite_moves[move] + opposite_dirs[md]

def add_perspecial_comms(solns, setups, inter, bf, t1):
    for setup in setups:
        insertion = f"{mirror(setup)} {inter} {setup} {inter} {inverse_moves(mirror(setup))}"
        comm = f"[{insertion}, {inter}]"
        if do_moves(bf, comm_to_moves(comm)) == t1:
            solns.append(comm)
        else:
            solns.append(inverse_comm(comm))


def search_per_special(bf, t1, t2):
    """
    Generate 6 unique comms for Per Special case
    """
    solns = []

    # Interchange on bf and t1
    inter = get_interchange(bf, t1) 
    moveset = [x for x in single_moves if x != inter[0] and x != opposite_moves[inter[0]]]
    # Find 2 single moves that get t2 into interchange layer
    setups = get_perspecial_setups(t2, inter[0], moveset)
    add_perspecial_comms(solns, setups, inter, bf, t1)
    
    # Interchange on t1 and t2
    inter = get_interchange(t1, t2) 
    moveset = [x for x in single_moves if x != inter[0] and x != opposite_moves[inter[0]]]
    # Find 2 single moves that get bf into interchange layer
    setups = get_perspecial_setups(bf, inter[0], moveset)
    add_perspecial_comms(solns, setups, inter, bf, t1)

    # Interchange on t2 and bf
    inter = get_interchange(t2, bf) 
    moveset = [x for x in single_moves if x != inter[0] and x != opposite_moves[inter[0]]]
    # Find 2 single moves that get t1 into interchange layer
    setups = get_perspecial_setups(t1, inter[0], moveset)
    add_perspecial_comms(solns, setups, inter, bf, t1)

    return solns

def get_bh_comms(bf, t1, t2):
    commtype = classify_comm(bf, t1, t2)
    if commtype == "Per Special":
        solns = search_per_special(bf, t1, t2)
    if commtype == "Cyclic Shift":
        solns = search_cyclic_shift(bf, t1, t2)
    if commtype == "Orthogonal" or commtype == "A9":
        solns = search_opt_1move_setup(bf, t1, t2)
    if commtype == "Columns":
        solns = search_opt_2move_setup(bf, t1, t2)
        solns += search_1move_cyclic_shift(bf, t1, t2)
    if commtype == "Pure":
        solns = search_pure_comm(bf, t1, t2)
    return list(set(solns))


if __name__ == "__main__":
    #bf, t1, t2 = input("Enter targets: ").split()
    #inter = get_interchange(t1, t2)
    """
    print(get_interchange(t1, t2))
    print(get_piece_dist(t1, t2))
    print(is_ani(t1, t2))
    print(is_opi(t1, t2))
    print(get_common_face(bf, t1 ,t2))
    print()
    print(classify_comm(bf, t1, t2))
    print(inter)
    print(search_insertion(bf, t1, inter))
    print(search_insertion(bf, t2, inter))
    """
    """
    solns = search_pure_comm(bf, t1, t2)
    for soln in solns:
        print(soln)
    """
    bf = input("Enter buffer: ")
    npu = 0
    nor = 0
    ncs = 0
    nps = 0
    nco = 0
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
                        solns = search_pure_comm(bf, p1, p2)
                        if len(solns) > 0:
                            npu += 1
                            """
                            print(f"{bf} {p1} {p2}: ", end = '')
                            for soln in solns:
                                print(soln, end=', ' if soln != solns[-1] else '') 
                            print()
                            """
                            #print(f"{bf} {p1} {p2}: {comm_to_moves(solns[0])}")

                        # add other comm types
                        commtype = classify_comm(bf, p1, p2)
                        if commtype == "Per Special":
                            nps += 1
                            solns = search_per_special(bf, p1, p2)
                            print(f"{bf} {p1} {p2}: {solns}")
                        if commtype == "Cyclic Shift":
                            ncs += 1
                            #solns = search_cyclic_shift(bf, p1, p2)
                            #print(f"{bf} {p1} {p2}: {comm_to_moves(solns[0])}")
                        if commtype == "Orthogonal":
                            nor += 1
                            #solns = search_opt_1move_setup(bf, p1, p2)
                            #print(f"{bf} {p1} {p2}: {comm_to_moves(solns[0])}")
                            
                            #print(f"{bf} {p1} {p2}: ", end = '')
                            #for soln in solns:
                            #    print(soln, end=', ' if soln != solns[-1] else '') 
                            #print()
                        if commtype == "Columns":
                            #solns = search_1move_cyclic_shift(bf, p1, p2)
                            #solns = search_opt_2move_setup(bf, p1, p2)
                            #print(f"{bf} {p1} {p2}: {solns}")
                            nco += 1

    print()     
    print(f"{npu} pure comms")
    print(f"{nps} per specials")
    print(f"{ncs} cyclic shifts")
    print(f"{nor} orthogonals")
    print(f"{nco} columns")
    print(f"{378-npu-nps-ncs-nor-nco} A9s")

    