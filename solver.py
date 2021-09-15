
import re
from cube import do_moves, single_moves, opposite_moves, opposite_dirs, pieces, get_piece_idx
from cube_moves import comm_to_moves, inverse_comm, get_comm_parts

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
    return not is_inter(t1, t2) and is_opp(t1,t2)

def is_coplanar(t1, t2, t3):
    return get_common_face(t1, t2, t3) is not None

def classify_comm(bf, t1, t2):
    """
    Basic classification of comms without searching for insertions, only filters out 
    Per Special, Cyclic Shift and Orthogonal comms.
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
    # Else, is Pure/A9/Columns
    return "Pure/A9/Columns"

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

def search_1move_setup(bf, t1, t2):
    is_a9_optimal = False
    solns = []
    for setup in single_moves:
        for setd in ["", "'", "2"]:
            nbf, nt1, nt2 = do_moves(bf, setup+setd), do_moves(t1, setup+setd), do_moves(t2, setup+setd)
            pure_solns = search_pure_comm(nbf, nt1, nt2)
            for soln in pure_solns:
                # Found A9, remove all 10 move solns as they are no longer optimal
                soln = f"[{setup+setd}: {soln}]"
                parts = get_comm_parts(soln)
                if setup == parts['insertion'][0] or setup == parts['interchange'][0]:
                    if not is_a9_optimal:
                        solns.clear()
                        is_a9_optimal = True
                    solns.append(soln)
                else:
                    if not is_a9_optimal:
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
    

def get_bh_comm(buffer, t1, t2):
    pass

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
                        if commtype == "Cyclic Shift":
                            ncs += 1
                        if commtype == "Orthogonal":
                            nor += 1
                            solns = search_1move_setup(bf, p1, p2)
                            print(f"{bf} {p1} {p2}: {comm_to_moves(solns[0])}")
                            
                            #print(f"{bf} {p1} {p2}: ", end = '')
                            #for soln in solns:
                            #    print(soln, end=', ' if soln != solns[-1] else '') 
                            #print()

    print()     
    print(f"{npu} pure comms")
    print(f"{nps} per specials")
    print(f"{ncs} cyclic shifts")
    print(f"{nor} orthogonals")

    