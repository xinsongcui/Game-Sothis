
if __name__ == "__main__":
    dir = "/home/chengjerry/Documents/code/Game-Sothis/data_labeling/query_results/jerry_queries/unknown worlds.csv"
    result = ""
    with open(dir, 'r') as f:
        for line in f:
            if ",search_score_gt" in line:
                result += line
                continue
            elif ",2" in line:
                result += line
                continue

            result += line.replace("\n", ",2\n")
    
    with open(dir, "w+") as f:
        f.write(result)

