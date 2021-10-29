import torch
from torch_geometric.data import Data, Batch, DataLoader

def get_pytorch_graph_(embeddings, graphs):

    # print('embeddings.size()', embeddings.size())
    # print('len graphs', len(graphs))
    # exit()

    list_geometric_data = []

    # for each b in batch
    for idx, emb in enumerate(embeddings):
        #print(idx)
        edges_index = graphs[idx][0]
        edges_types = graphs[idx][1]
        #print(edges_index)

        data = Data(x=emb, edge_index=edges_index, y=edges_types)
        list_geometric_data.append(data)

    #print('len list', len(list_geometric_data))
    bdl = Batch.from_data_list(list_geometric_data)

    bdl = bdl.to('cuda:' + str(torch.cuda.current_device()))

    return bdl


def get_pytorch_graph(embeddings, graphs):

    # print('embeddings.size()', embeddings.size())
    # print('len graphs', len(graphs))
    # exit()

    list_geometric_data = [Data(x=emb, edge_index=graphs[idx][0], y=graphs[idx][1]) for idx, emb in enumerate(embeddings)]

    #print('len list', len(list_geometric_data))
    bdl = Batch.from_data_list(list_geometric_data)
    bdl = bdl.to('cuda:' + str(torch.cuda.current_device()))

    return bdl