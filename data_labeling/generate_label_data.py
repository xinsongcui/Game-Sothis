
import os
import pandas as pd
import pyterrier as pt

from utils import read_washed_data

def read_queries(qf_path):
    result = list()
    with open(qf_path, 'r') as f:
        for line in f:
            if "*" in line:
                line = line.replace("*", "").strip()
                result.append(line)
    return result

def get_pseudo_relevants(save_path, queries, br_models, data_dict):
    for q in queries:
        rlst = list()
        for br in br_models:
            rlst.append(br.search(q)[:25])
        
        result_df = pd.concat(rlst)
        result_df.drop_duplicates(subset=["docno"])

        result_df["name"] = result_df.docno.map(data_dict)

        fname = q + ".csv"
        fpath = os.path.join(save_path, fname)
        result_df.to_csv(fpath)
    return 


if __name__ == "__main__":
    if not pt.started():
        pt.init()
    
    data_df = read_washed_data("../washed_game_data.csv")
    docno_col = ['d' + str(i) for i in range(len(data_df))]
    data_df.insert(0, "docno", docno_col)

    data_dict = dict(zip(data_df.docno, data_df.name))

    all_queries = read_queries("meeting_1105.md")
    xinsong_queries = read_queries("xinsong_query.md")
    jerry_queries = list(set(all_queries) - set(xinsong_queries))

    xinsong_rpath = "query_results/xinsong_queries"
    jerry_rpath = "query_results/jerry_queries"

    index_dir = "./game_index_dir"
    

    if not os.path.exists(os.path.join(index_dir, "data.properties")):
        indexer = pt.DFIndexer(index_dir, overwrite=True, tokeniser="UTFTokeniser")
        index_ref = indexer.index(data_df["summary"], data_df["name"], data_df["date"], data_df["genre"], data_df["docno"])
    else:
        index_ref = pt.IndexRef.of(index_dir + "/data.properties")
    
    index = pt.IndexFactory.of(index_ref)

    bm25 = pt.BatchRetrieve(index, wmodel="BM25")
    tfidf = pt.BatchRetrieve(index, wmodel="TF_IDF")
    pl2 = pt.BatchRetrieve(index, wmodel="PL2")
    In_expB2 = pt.BatchRetrieve(index, wmodel="In_expB2")

    all_br = [bm25, tfidf, pl2, In_expB2]

    get_pseudo_relevants(xinsong_rpath, xinsong_queries, all_br, data_dict)
    get_pseudo_relevants(jerry_rpath, jerry_queries, all_br, data_dict)

