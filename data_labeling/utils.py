
import os
import pandas as pd

def wash_csv(data_path):
    result_str = ""
    with open(data_path, 'r') as f:
        f_str = f.read()
        in_str_flag = False
        space_counter = 0
        for l in f_str:
            
            if l == '"':
                in_str_flag = not in_str_flag

            if in_str_flag and l in ('\n', '\t', ' '):
                if l == ' ':
                    space_counter += 1
                continue
            if space_counter != 0 and l != ' ':
                space_counter = 0
                result_str += ' '
            result_str += l
    
    data_fhead, data_fbase = os.path.split(data_path)
    data_fbase = "washed_" + data_fbase
    with open(os.path.join(data_fhead, data_fbase), "w+") as f:
        f.write(result_str)
    return 

def read_washed_data(data_path):
    with open(data_path, 'r') as f:
        tmp_df = pd.read_csv(f)
    return tmp_df

if __name__ == "__main__":
    wash_csv("../game_data.csv")
    data_df = read_washed_data("../washed_game_data.csv")
    print("DEBUG", len(data_df))
    print(data_df)
    


