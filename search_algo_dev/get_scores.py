import os
import pandas as pd
import numpy as np
import pyterrier as pt
from matplotlib import pyplot as plt
from collections import Counter


from utils import read_washed_data

def get_largest_count(all_topics:dict) -> int:
    sorted_qid = sorted(all_topics.values())
    if len(sorted_qid) == 0:
        return 0
    else:
        largest_qid = sorted_qid[-1]
        return int(largest_qid.replace("q", "")) +1

def read_queries(all_topics, all_qrels, query_path, name_docno_dict, scale=5):
    
    counter = get_largest_count(all_topics)
    rels_scale_map = {2:5, 1:2, 0:0}
    num_docs = len(name_docno_dict.values())

    tmp_scores = np.zeros((num_docs, ))

    for fname in os.listdir(query_path):
        if fname.endswith(".csv"):
            query_name = fname.replace(".csv", "")
            if query_name not in all_topics.keys():
                all_topics[query_name] = "q" + str(counter)
                counter += 1
            
            qid = all_topics[query_name]
            csv_df = pd.read_csv(os.path.join(query_path, fname), header=0, sep='\s*,\s*', engine='python')

            if "relevance" not in csv_df.columns.tolist():
                print("DEBUG col names", query_name)
                print("DEBUG col names", csv_df.columns.tolist())
            name_relevance_df = csv_df[["name", "relevance"]]
            name_relevance_df = name_relevance_df.drop_duplicates(subset="name")

            
            qid_col = [qid] * num_docs
            # tmp_scores = np.zeros((num_docs, ))
            tmp_df = pd.DataFrame({"qid":qid_col, "docno":list(name_docno_dict.values()), "label":tmp_scores.copy(), "iteration":tmp_scores.copy()})
            

            for index, row in name_relevance_df.iterrows():
                name_tmp, rels_tmp = row["name"], row["relevance"]
                # print("DEBUG what is rels_tmp", rels_tmp, type(rels_tmp))
                rels_tmp = int(rels_tmp) 
                if scale == 2:
                    rels_tmp = rels_scale_map[rels_tmp]

                docno_tmp = name_docno_dict[name_tmp]
                # idx = tmp_df.loc[tmp_df["docno"] == docno_tmp]
                tmp_df.loc[tmp_df["docno"] == docno_tmp, "label"] = rels_tmp

            all_qrels = pd.concat([all_qrels, tmp_df], ignore_index=True)
    return all_qrels
        

if __name__ == "__main__":

    if not pt.started():
        pt.init()

    query_path_collection = [
            ("../data_labeling/query_results/jerry_queries", 2),
            ("../data_labeling/query_results/xinsong_queries", 5)
            ]
    
    data_df = read_washed_data("../washed_game_data.csv")
    docno_col = ['d' + str(i) for i in range(len(data_df))]
    data_df.insert(0, "docno", docno_col)

    name_docno_dict = dict(zip(data_df.name, data_df.docno))
    
    # read_queries(all_query, query_path)
    all_topics_dict = dict()
    all_qrels = pd.DataFrame(columns=['qid', 'docno', 'label', "iteration"])
    for qp, scl in query_path_collection:
        all_qrels = read_queries(all_topics_dict, all_qrels, qp, name_docno_dict, scale=scl)

    all_topics = pd.DataFrame({"qid":list(all_topics_dict.values()), "query":list(all_topics_dict.keys())})

    # print(all_topics.head(5))
    # print(all_qrels.head(5))
    all_qrels = all_qrels.astype({"label":"int"})

    index_dir = "./game_index_dir"

    if not os.path.exists(os.path.join(index_dir, "data.properties")):
        indexer = pt.DFIndexer(index_dir, overwrite=True, tokeniser="UTFTokeniser")
        index_ref = indexer.index(data_df["summary"], data_df["name"], data_df["date"], data_df["genre"], data_df["docno"])
    else:
        index_ref = pt.IndexRef.of(index_dir + "/data.properties")

    index = pt.IndexFactory.of(index_ref)

    bm25 = pt.BatchRetrieve(index, wmodel="BM25")
    tfidf = pt.BatchRetrieve(index, wmodel="TF_IDF")
    random_scorer = lambda keyFreq, posting, entryStats, collStats: 0
    rand_retr = pt.BatchRetrieve(index, wmodel=random_scorer)

    exp_result = pt.Experiment(
                            [rand_retr, bm25, tfidf],
                            all_topics,
                            all_qrels,
                            eval_metrics=["map", "ndcg", "ndcg_cut_5", "ndcg_cut_10"])
    print(exp_result)
    
    # all_ratings = all_qrels["label"].to_list()
    # rate_count = dict(Counter(all_ratings))

    # rate_count.pop(0)

    # total_rated = sum(rate_count.values())
    # percent_rated = dict()
    # for k in rate_count:
    #     percent_rated[k] = rate_count[k] / total_rated
    # print(percent_rated)
    
    # rate_lbs = ["Rated "+str(i) for i in rate_count.keys()]
    # rated_percent_vals = rate_count.values()
    # fig1, ax1 = plt.subplots()
    # ax1.pie(rated_percent_vals, labels=rate_lbs, autopct='%1.1f%%', shadow=True, startangle=0)
    # ax1.axis("equal")
    # ax1.set_title("Percentage of rated documents")

    # fig1.savefig("percentage_of_rated_content.png")
    # x_axis = ["map", "ndcg", "ndcg@5", "ndgc@10"]
    # rand_retr_result = [0.633344, 0.667198, 0.611389, 0.613880]
    # bm25_result = [0.732402, 0.758720, 0.731213, 0.741592]
    # tfidf_result = [0.713821, 0.747085, 0.721493, 0.725219]
    # fig, ax = plt.subplots()
    # x_range = np.arange(len(x_axis))

    # ax.bar(x_range-0.2, rand_retr_result, width=0.2, label="random")
    # ax.bar(x_range, bm25_result, width=0.2, label="BM25")
    # ax.bar(x_range+0.2, tfidf_result, width=0.2, label="TF-IDF")

    # ax.set_xticks(x_range, x_axis)
    # ax.set_ylim(0.5)
    # ax.set_title("Baseline Performance")
    # ax.legend()
    # ax.set_xlabel("Evaluation Methods")
    # ax.set_ylabel("Performance")
    
    # fig.savefig("baseline_performance.png")


    