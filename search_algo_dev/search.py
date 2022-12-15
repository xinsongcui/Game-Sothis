import os
import pandas as pd
import numpy as np
import pyterrier as pt
from matplotlib import pyplot as plt
from collections import Counter
import fastrank
from sklearn.ensemble import RandomForestRegressor
from matplotlib import pyplot as plt


from get_scores import read_queries
from utils import read_washed_data

if __name__ == "__main__":
    
    if not pt.started():
        pt.init()

    query_path_collection = [
            ("../data_labeling/query_results/jerry_queries", 2),
            ("../data_labeling/query_results/xinsong_queries", 5)
            ]
    index_dir = "../data_labeling/game_index_dir"
    data_df = read_washed_data("../washed_game_data.csv")
    data_df["userscore"] = data_df["userscore"].astype(str)

    RANK_CUTOFF = 15
    SEED = 42

    train_request = fastrank.TrainRequest.coordinate_ascent()

    params = train_request.params
    params.init_random = True
    params.normalize = True
    params.seed = 1234567

    docno_col = ['d' + str(i) for i in range(len(data_df))]
    data_df.insert(0, "docno", docno_col)

    name_docno_dict = dict(zip(data_df.name, data_df.docno))
    
    # read_queries(all_query, query_path)
    all_topics_dict = dict()
    all_qrels = pd.DataFrame(columns=['qid', 'docno', 'label', "iteration"])
    for qp, scl in query_path_collection:
        all_qrels = read_queries(all_topics_dict, all_qrels, qp, name_docno_dict, scale=scl)

    all_topics = pd.DataFrame({"qid":list(all_topics_dict.values()), "query":list(all_topics_dict.keys())})
    all_qrels = all_qrels.astype({"label":"int"})


    if not os.path.exists(os.path.join(index_dir, "data.properties")):
        indexer = pt.DFIndexer(index_dir, overwrite=True, tokeniser="UTFTokeniser", stopwords='terrier')
        index_ref = indexer.index(data_df["summary"], data_df["name"], data_df["date"], data_df["genre"], data_df["userscore"], data_df["docno"])
    else:
        index_ref = pt.IndexRef.of(index_dir + "/data.properties")

    index = pt.IndexFactory.of(index_ref)

    bm25 = pt.BatchRetrieve(index, wmodel="BM25")
    tfidf = pt.BatchRetrieve(index, wmodel="TF_IDF")
    random_scorer = lambda keyFreq, posting, entryStats, collStats: 0
    rand_retr = pt.BatchRetrieve(index, wmodel=random_scorer)

    game_sothis_features = (tfidf % RANK_CUTOFF) >> pt.text.get_text(index, ["name", "date", "genre", "userscore"]) >> (
            pt.transformer.IdentityTransformer()
            **
            (pt.text.scorer(body_attr="name", takes='docs', wmodel='TF_IDF', stopwords=None, stemmer=None))
            ** 
            (pt.apply.doc_score(lambda row: float(row["userscore"])))
            # ** 
            # (pt.apply.doc_score(lambda row: int("2017" in row["date"])))
            # ** 
            # (pt.text.scorer(body_attr="genre", takes='docs', wmodel='CoordinateMatch', stopwords=None, stemmer=None))
            # **
            # (pt.text.scorer(body_attr="date", takes='docs', wmodel='BM25'))
            ** # abstract coordinate match
            pt.BatchRetrieve(index, wmodel="CoordinateMatch")
        )
    sname = ["random", "bm25", "tfidf", "game-sothis"]
    fname = ["name", "userscore", "date"]

    feature_exp = pt.Experiment(
        [game_sothis_features >> pt.ltr.feature_to_score(i) for i in range(len(fname))],
            all_topics,
            all_qrels, 
            names=fname,
            eval_metrics=["map", "ndcg", "ndcg_cut_10", "num_rel_ret", ])
    # print(game_sothis_features.search("action"))
    print(feature_exp.to_markdown())

    exp_result = pt.Experiment(
                            [rand_retr, bm25, tfidf, game_sothis_features],
                            all_topics,
                            all_qrels,
                            eval_metrics=["map", "ndcg", "ndcg_cut_5", "ndcg_cut_10"])
    print(exp_result.to_markdown())

    # fig= plt.figure()
    # ax0 = fig.add_subplot(111)
    # ax0.bar(np.arange(len(fname)), game_sothis_features[1].model.to_dict()['Linear']['weights'])
    # ax0.set_xticks(np.arange(len(fname)))
    # ax0.set_xticklabels(fname, rotation=45, ha='right')
    # ax0.set_title("Feature Weights")
    # ax0.set_yscale('log')
    # fig.savefig("feature_weights.png")