import os
import sys
import random
from tqdm import tqdm
dir_path = os.path.dirname(os.path.realpath(__file__))

folder = sys.argv[1]

new_tokens_amr = set([':example', ':range', ':d', ':degree-of', ':polarity', ':path', ':prep-from', ':source', ':purpose-of', ':frequency', ':ARG4-of', ':medium-of', ':consist-of', ':instrument', ':value-of', ':prep-to', ':)', ':op24', ':-P', ':quant-of', ':prep-on', ':location-of', ':purpose', ':op3', ':s', ':op20', ':time-of', ':snt1', ':ARG1-of', ':destination-of', ':ord', ':concession-of', ':century', ':medium', ':prep-against', ':op18', ':op21', ':prep-along-with', ':manner-of', ':ARG9', ':op13', ':frequency-of', ':topic-of', ':prep-among', ':snt10', ':degree', ':condition', ':season', ':op10', ':op7', ':op8', ':polarity-of', ':ARG8', ':prep-as', ':ord-of', ':prep-in', ':snt8', ':name-of', ':topic', ':prep-with', ':calendar', ':path-of', ':wiki', ':accompanier-of', ':ARG3-of', ':ARG3', ':op17', ':snt3', ':ARG5-of', ':era', ':part-of', ':op1-of', ':weekday', ':subset', ':mode', ':ARG2-of', ':age-of', ':op9', ':quarter', ':op1', ':ARG2', ':direction', ':name', ':polite', ':snt9', ':op11', ':op22', ':condition-of', ':duration-of', ':prep-toward', ':snt11', ':prep-for', ':prep-into', ':op2', ':op19', ':li', ':ARG1', ':op14', ':month', ':prep-under', ':ARG6-of', ':prep-on-behalf-of', ':prep-by', ':ARG6', ':value', ':day', ':extent', ':source-of', ':concession', ':example-of', ':subevent', ':destination', ':poss-of', ':snt2', ':op5', ':op16', ':ARG7', ':prep-in-addition-to', ':op12', ':ARG5', ':part', ':duration', ':subevent-of', ':manner', ':mod', ':beneficiary-of', ':beneficiary', ':op6', ':dayperiod', ':prep-at', ':year2', ':accompanier', ':location', ':snt6', ':age', ':domain', ':ARG0', ':conj-as-if', ':ARG4', ':P', ':prep-amid', ':unit', ':ARG7-of', ':snt4', ':op23', ':poss', ':extent-of', ':decade', ':year', ':direction-of', ':quant', ':op4', ':prep-without', ':scale', ':subset-of', ':snt7', ':prep-out-of', ':time', ':instrument-of', ':timezone', ':snt5', ':op15', ':ARG0-of'])

from transformers import T5Tokenizer
tokenizer = T5Tokenizer.from_pretrained("t5-base")
new_tokens_vocab = {}
new_tokens_vocab['additional_special_tokens'] = []
for idx, t in enumerate(new_tokens_amr):
    new_tokens_vocab['additional_special_tokens'].append(t)
num_added_toks = tokenizer.add_special_tokens(new_tokens_vocab)
tokenizer.unique_no_split_tokens.sort(key=lambda x: -len(x))
# print(self.tokenizer.unique_no_split_tokens)
print('We have added tokens', num_added_toks)

def open_file(f):
    return open(f, 'r').readlines()

def convert_graph(file_souce, file_graph):

    mappings = []
    amr_toks = []

    amr_toks_len = []

    for l_idx, l in enumerate(tqdm(file_souce)):

        l = l.strip()


        # TODO: this datapoint makes the alignment to break.
        url = 'http://articles.cnn.com/2011-04-13/politics/obama.deficits_1_spending-cuts-deficit-reduction-tax-hikes?_s=PM:POLITICS'
        if url in l:
            l = l.replace(url, 'articles.cnn.com')

        map = {}
        amr = l.split()
        amr_tok = tokenizer.tokenize(l)
        amr_toks_len.append(len(amr_tok))

        idx_original = 0
        for idx, token in enumerate(amr_tok):

            if token in new_tokens_amr:
                map[idx_original] = [idx]
                idx_original += 1
            elif token.startswith('▁'):
                map[idx_original] = [idx]
                idx_original += 1
            else:
                map[idx_original - 1].append(idx)

        try:
            assert (len(amr) == max(map.keys()) + 1)
            assert (len(amr_tok) == max(max(v) for v in map.values()) + 1)
        except:
            print(l_idx)
            print(l)
            print(" ")
            print(amr)
            print(amr_tok)
            print(len(amr), len(amr_tok))
            print(map)
            for k, v in map.items():
                print(amr[k], "     ", ' '.join(amr_tok[vv] for vv in v))
            exit()

        mappings.append(map)
        amr_toks.append(' '.join(amr_tok))

    assert len(mappings) == len(file_souce) == len(amr_toks) == len(amr_toks_len)

    new_graphs = []
    for l_idx, l in enumerate(tqdm(file_graph)):
        src_graphs = l.strip()

        edges = src_graphs.split()
        new_edges = []

        for e in edges:
            e = e.replace("(", "")
            e = e.replace(")", "")
            e = e.split(",")
            e1 = int(e[0])
            e2 = int(e[1])
            r = e[2]
            try:
                assert amr_toks_len[l_idx] > mappings[l_idx][e1][0]
                assert amr_toks_len[l_idx] > mappings[l_idx][e2][0]
                #new_edges.append('(' + str(mappings[l_idx][e1][0]) + ',' + str(mappings[l_idx][e2][0]) + ',' + r + ')')
            except:
                print(amr_toks_len[l_idx])
                print(l_idx, e1, e2)
                print(mappings[l_idx])
                print(amr_toks[l_idx])
                print(l["src_texts"].split())
                print(len(l["src_texts"].split()))
                print(l["src_graphs"])
                exit()


            for idx, ee1 in enumerate(mappings[l_idx][e1]):
                for idx, ee2 in enumerate(mappings[l_idx][e2]):
                    new_edges.append('(' + str(ee1) + ',' + str(ee2) + ',' + r + ')')
        new_edges = ' '.join(new_edges)
        new_graphs.append(new_edges)

    assert len(mappings) == len(file_graph) == len(amr_toks) == len(new_graphs) == len(amr_toks_len)

    return new_graphs, amr_toks_len

graph_files = ['train.graph', 'test.graph',  'val.graph']
source_files = ['train.source', 'test.source',  'val.source']

for s,g in zip(source_files, graph_files):
    print(g)
    s_data =  open_file(folder + s)
    g_data = open_file(folder + g)
    new_graph, amr_toks_len = convert_graph(s_data,g_data)

    new_graph_file = open(folder + g + '.tok', 'w')
    for ng in new_graph:
        new_graph_file.write(ng + "\n")







