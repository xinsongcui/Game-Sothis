import os
import pandas as pd

def get_largest_count(all_topics:dict) -> int:
    largest_qid = sorted(all_topics.values())[-1]
    return int(largest_qid.replace("q", "")) +1

def read_queries(all_topics, all_qrels, query_path):
    counter = get_largest_count(all_topics)
    for fname in os.listdir(query_path):
        if fname.endswith(".csv"):
            query_name = fname.replace(".csv", "")
            if query_name not in all_topics.keys():
                all_topics[query_name] = "q" + str(counter)
                counter += 1
            
            qid = all_topics[query_name]
            
            

            
    


if __name__ == "__main__":
    all_query = dict()
    query_path = "/home/chengjerry/Documents/code/Game-Sothis/data_labeling/query_results/jerry_queries"
    read_queries(all_query, query_path)

    