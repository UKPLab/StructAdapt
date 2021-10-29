"""
Preprocess AMR and surface forms.

Options:

- linearise: for seq2seq learning
  - simplify: simplify graphs and lowercase surface
  - anon: same as above but with anonymisation
  
- triples: for graph2seq learning
  - anon: anonymise NEs

"""
from amr import AMR, Var
import re
import json
import argparse
import  penman
from penman.model import Model

def simplify_old(tokens, v2c):

    mapping = {}
    new_tokens = []
    for tok in tokens:
        # ignore instance-of
        if tok.startswith('('):
            #new_tokens.append('(')
            last_map = tok.replace("(", "")
            continue
        elif tok == '/':
            save_map = True
            continue
        # predicates, we remove any alignment information and parenthesis
        elif tok.startswith(':'):

            new_tok = tok.strip(')')
            new_tok = new_tok.split('~')[0]
            new_tokens.append(new_tok)

            # count_ = tok.count(')')
            # for _ in range(count_):
            #     new_tokens.append(')')

        # concepts/reentrancies, treated similar as above
        else:
            new_tok = tok.strip(')')
            new_tok = new_tok.split('~')[0]
            # now we check if it is a concept or a variable (reentrancy)
            if Var(new_tok) in v2c:
                # reentrancy: replace with concept
                if new_tok not in mapping:
                    mapping[new_tok] = set()
                mapping[new_tok].add(len(new_tokens))
                # except:
                #     print(new_tokens)
                #     print(" ".join(tokens))
                #     print(new_tok)
                #     print(mapping)
                #     print("xx")
                #     exit()
                new_tok = v2c[Var(new_tok)]._name


            # remove sense information
            elif re.search(SENSE_PATTERN, new_tok):
                new_tok = new_tok[:-3]
            # remove quotes
            elif new_tok[0] == '"' and new_tok[-1] == '"':
                new_tok = new_tok[1:-1]
            new_tokens.append(new_tok)

            if save_map:
                if last_map not in mapping:
                    mapping[last_map] = set()

                mapping[last_map].add(len(new_tokens) - 1)
                save_map = False

            # count_ = tok.count(')')
            # for _ in range(count_):
            #     new_tokens.append(')')

    return new_tokens, mapping


def simplify_2(tokens, v2c):

    mapping = {}
    new_tokens = []
    for idx, tok in enumerate(tokens):
        # ignore instance-of
        if tok.startswith('('):
            #new_tokens.append('(')
            last_map = tok.replace("(", "")
            continue
        elif tok == '/':
            save_map = True
            continue
        # predicates, we remove any alignment information and parenthesis
        elif tok.startswith(':'):

            new_tok = tok.strip(')')
            new_tok = new_tok.split('~')[0]
            new_tokens.append(new_tok)

            # count_ = tok.count(')')
            # for _ in range(count_):
            #     new_tokens.append(')')

        # concepts/reentrancies, treated similar as above
        else:
            new_tok = tok.strip(')')
            new_tok = new_tok.split('~')[0]

            if new_tok == "":
                continue

            # now we check if it is a concept or a variable (reentrancy)
            if new_tok in v2c:
                # reentrancy: replace with concept
                if new_tok not in mapping:
                    mapping[new_tok] = set()
                mapping[new_tok].add(len(new_tokens))

                if v2c[new_tok] is not None:
                    new_tok = v2c[new_tok]


            # check number
            elif new_tok.isnumeric():
                new_tok = new_tok
            # remove sense information
            elif re.search(SENSE_PATTERN, new_tok):
                new_tok = new_tok[:-3]
            # remove quotes
            elif new_tok[0] == '"' and new_tok[-1] == '"':
                new_tok = new_tok[1:-1]

            if new_tok != "":
                new_tokens.append(new_tok)

            if save_map:
                if last_map not in mapping:
                    mapping[last_map] = set()

                mapping[last_map].add(len(new_tokens) - 1)
                save_map = False


    return new_tokens, mapping


def get_name(v, v2c):
    try:
        # Remove sense info from concepts if present
        c = v2c[v]
        if re.search(SENSE_PATTERN, c._name):
            return c._name[:-3]
        else:
            return c._name
    except: # constants: remove quotes if present
        #r = str(v).lower()
        r = str(v)
        if r[0] == '"' and r[-1] == '"':
            return r[1:-1]
        else:
            return r


def get_edge(tokens, edge, edge_id, triple, mapping, graph):
    for idx in range(edge_id + 1, len(tokens)):
        if tokens[idx] == edge:
            return idx

    print(tokens)
    print(len(tokens))
    print(triple)
    print(graph.triples)
    print(mapping)
    print(edge, edge_id)
    print("error edge")
    exit()

def get_positions(new_tokens, src):
    pos = []
    for idx, n in enumerate(new_tokens):
        if n == src:
            pos.append(idx)

    return pos


def get_line_graph_new(graph, new_tokens, mapping, roles_in_order, amr):
    triples = []
    nodes_to_print = new_tokens

    graph_triples = graph.triples

    edge_id = -1
    triples_set = set()
    count_roles = 0
    for triple in graph_triples:
        src, edge, tgt = triple

        #try:

        if edge == ':instance' or edge == ':instance-of':
            continue

        #print(triple)

        # if penman.layout.appears_inverted(graph_penman, v):
        if "-of" in roles_in_order[count_roles]:
            edge = edge + "-of"
            old_tgt = tgt
            tgt = src
            src = old_tgt

        #print(roles_in_order, count_roles, edge)
        assert roles_in_order[count_roles] == edge

        count_roles += 1

        if edge == ':wiki':
            continue

        # process triples
        src = str(src).replace("\"", "")
        tgt = str(tgt).replace("\"", "")



        try:
            if src not in mapping:
                src_id = get_positions(new_tokens, src)
            else:
                src_id = sorted(list(mapping[src]))
            # check edge to verify
            edge_id = get_edge(new_tokens, edge, edge_id, triple, mapping, graph)

            if tgt not in mapping:
                tgt_id = get_positions(new_tokens, tgt)
            else:
                tgt_id = sorted(list(mapping[tgt]))
        except:
            print(graph_triples)
            print(src, edge, tgt)
            print("error in the mapping")

            print(" ".join(new_tokens))
            exit()

        for s_id in src_id:
            if (s_id, edge_id, 'd') not in triples_set:
                triples.append((s_id, edge_id, 'd'))
                triples_set.add((s_id, edge_id, 'd'))
                triples.append((edge_id, s_id, 'r'))
        for t_id in tgt_id:
            if (edge_id, t_id, 'd') not in triples_set:
                triples.append((edge_id, t_id, 'd'))
                triples_set.add((edge_id, t_id, 'd'))
                triples.append((t_id, edge_id, 'r'))

    if nodes_to_print == []:
        # single node graph, first triple is ":top", second triple is the node
        triples.append((0, 0, 's'))
    return nodes_to_print, triples

def get_line_graph(graph, new_tokens, mapping, tokens):
    triples = []
    uniq = 0
    nodes_to_print = new_tokens

    graph_triples = graph.triples()

    v2c = graph.var2concept()


    edge_id = 0
    triples_set = set()
    for triple in graph_triples:
        src, edge, tgt = triple
        if edge == ':top':
            # store this to add scope later
            top_node = get_name(tgt, v2c)
            continue
        if edge == ':instance-of' or edge == ':wiki':
        #if edge == ':instance-of':
            continue
        # process triples
        src = str(src).replace("\"", "")
        tgt = str(tgt).replace("\"", "")

        try:
            if src not in mapping:
                src_id = get_positions(new_tokens, src)
            else:
                src_id = sorted(list(mapping[src]))
            # check edge to verify
            edge_id = get_edge(new_tokens, edge, edge_id)

            if tgt not in mapping:
                tgt_id = get_positions(new_tokens, tgt)
            else:
                tgt_id = sorted(list(mapping[tgt]))
        except:
            print(src, edge, tgt)
            print("error")
            print(mapping)

            #print(graph_triples)
            print(" ".join(new_tokens))
            print(" ".join(tokens))
            exit()

        for s_id in src_id:
            for t_id in tgt_id:
                if (s_id, edge_id, 'd') not in triples_set:
                    triples.append((s_id, edge_id, 'd'))
                    triples_set.add((s_id, edge_id, 'd'))
                    #triples.append((edge_id, s_id, 'r'))
                if (edge_id, t_id, 'd') not in triples_set:
                    triples.append((edge_id, t_id, 'd'))
                    triples_set.add((edge_id, t_id, 'd'))
                    #triples.append((t_id, edge_id, 'r'))



    if nodes_to_print == []:
        # single node graph, first triple is ":top", second triple is the node
        triples.append((0, 0, 's'))
    return nodes_to_print, triples

                                       

##########################

def print_simplified(graph_triples, v2c):
    """
    Given a modified graph, prints the linearised, simplified version with scope markers.
    Taken from AMR code.
    """       
    s = []
    stack = []
    instance_fulfilled = None
    concept_stack_depth = {None: 0} # size of the stack when the :instance-of triple was encountered for the variable

    # Traverse the graph and build initial string
    for h, r, d in graph_triples + [(None,None,None)]:
        if r==':top':
            s.append('(')
            s.append(get_name(d, v2c))
            stack.append((h, r, d))
            instance_fulfilled = False
        elif r==':instance-of':
            instance_fulfilled = True
            concept_stack_depth[h] = len(stack)
        else:
            while len(stack)>concept_stack_depth[h]:
                h2, r2, d2 = stack.pop()
                if instance_fulfilled is False:
                    s.pop()
                    s.pop()
                    s.append(get_name(d2, v2c))
                else:
                    s.append(')')
                instance_fulfilled = None
            if d is not None:
                s.append(r)
                s.append('(')
                s.append(get_name(d, v2c))
                stack.append((h, r, d))
                instance_fulfilled = False

    #import ipdb; ipdb.set_trace()
    # Remove extra parenthesis when there's one token only between them
    final_s = []
    skip = False
    for i, token in enumerate(s[:-2]):
        if token == '(':
            if s[i+2] == ')':
                skip = True
            if not skip:
                final_s.append(token)
        elif token == ')':
            if not skip:
                final_s.append(token)
            skip = False
        else:
            final_s.append(token)
    # remove extra set of parenthesis
    final_s.append(s[-2])
    if len(s) == 3:
        # corner case: single node with two parenthesis
        return s[1:2]
    #print(s)
    return final_s[1:]
##########################

def create_set_instances(graph_penman):
    instances = graph_penman.instances()
    #print(instances)
    dict_insts = {}
    for i in instances:
        dict_insts[i.source] = i.target
    return dict_insts

def get_roles_penman(graph_triples, roles_in_order):

    roles_penman = []
    count_roles = 0
    for v in graph_triples:
        role = v[1]
        if role == ':instance' or role == ':instance-of':
            continue
        if "-of" in roles_in_order[count_roles]:
            role = role + "-of"
        roles_penman.append(role)
        count_roles += 1

    return roles_penman

import traceback
def main(args):

    # First, let's read the graphs and surface forms
    with open(args.input_amr) as f:
        amrs = f.readlines()
    with open(args.input_surface) as f:
        surfs = f.readlines()

    if args.triples_output is not None:
        triples_out_penman = open(args.triples_output, 'w')
        reentrances_file = open(args.triples_output.replace("graph","reentrances"), 'w')

    i = 0
    cont_error = 0
    total_g = 0
    count_instance = 0
    with open(args.output, 'w') as out, open(args.output_surface, 'w') as surf_out:
        for idx, (amr, surf) in enumerate(zip(amrs, surfs)):
            try:
                total_g += 1
                graph_penman = penman.decode(amr)

            except:
                cont_error += 1
                print('error', cont_error, '/', total_g)
                continue


            # Get variable: concept map for reentrancies
            #v2c = graph.var2concept()

            if args.mode == 'LINE_GRAPH':
                i += 1
                v2c_penman = create_set_instances(graph_penman)


                tokens = amr.split()

                try:
                    new_tokens, mapping = simplify_2(tokens, v2c_penman)
                except:
                    cont_error += 1
                    print('error', cont_error, '/', total_g)
                    continue


                reentrance = max([len(m) for m in mapping.values()])

                roles_in_order = []
                instance_true = False
                for token in amr.split():
                    if token.startswith(":"):
                        if token == ':instance-of':
                            instance_true = True
                            continue
                        roles_in_order.append(token.split("~")[0])

                if instance_true:
                    count_instance += 1
                try:
                    nodes, triples = get_line_graph_new(graph_penman, new_tokens, mapping, roles_in_order, amr)
                except Exception as e:
                    traceback.print_exc()
                    cont_error += 1
                    print('error', cont_error, '/', total_g)
                    continue
                triples = sorted(triples)
                try:
                    triples_out_penman.write(' '.join(['(%d,%d,%s)' % adj for adj in triples]) + '\n')
                except:
                    print(triples)
                    print("error triples penman")
                    exit()

                try:
                    out.write(' '.join(nodes) + '\n')
                    reentrances_file.write(str(reentrance) + '\n')
                except:
                    print(nodes)
                    print(amr)
                    print(graph_penman.instances())
                    exit()

                
            # Process the surface form
            surf_out.write(surf)

        #print('count_instance', count_instance)


###########################
            
if __name__ == "__main__":
    
    # Parse input
    parser = argparse.ArgumentParser(description="Preprocess AMR into linearised forms with multiple preprocessing steps (based on Konstas et al. ACL 2017)")
    parser.add_argument('input_amr', type=str, help='input AMR file')
    parser.add_argument('input_surface', type=str, help='input surface file')
    parser.add_argument('output', type=str, help='output file, either AMR or concept list')
    parser.add_argument('output_surface', type=str, help='output surface file')
    parser.add_argument('--mode', type=str, default='GRAPH', help='preprocessing mode',
                        choices=['GRAPH','LIN','LINE_GRAPH'])
    parser.add_argument('--anon', action='store_true', help='anonymise NEs and dates')
    parser.add_argument('--scope', action='store_true', help='add scope markers to graph')
    parser.add_argument('--add-reverse', action='store_true', help='whether to add reverse edges in the graph output')
    parser.add_argument('--triples-output', type=str, default=None, help='triples output for graph2seq')
    parser.add_argument('--map-output', type=str, default=None, help='mapping output file, if using anonymisation')
    parser.add_argument('--anon-surface', type=str, default=None, help='anonymized surface output file, if using anonymisation')
    parser.add_argument('--nodes-scope', type=str, default=None, help='anonymized AMR graph file, with scope marking, used in baseline seq2seq models')

    args = parser.parse_args()

    assert (args.triples_output is not None) or (args.mode != 'GRAPH'), "Need triples output for graph mode"
    assert (args.map_output is not None) or (not args.anon), "Need map output for anon mode"
    assert (args.anon_surface is not None) or (not args.anon), "Need anonymized surface output for anon mode"

    SENSE_PATTERN = re.compile('-[0-9][0-9]$')
    
    main(args)
