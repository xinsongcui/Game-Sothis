
if __name__ == "__main__":
    dir = "/home/chengjerry/Documents/code/Game-Sothis/data_labeling/query_results/xinsong_queries/2020.csv"
    result = ""
    with open(dir, 'r') as f:
        for line in f:
            if ",re" in line:
                result += line
                continue
            elif ",5" in line:
                result += line
                continue

            result += line.replace("\n", ",5\n")
    
    with open(dir, "w+") as f:
        f.write(result)

