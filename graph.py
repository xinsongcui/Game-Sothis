import json

game_list = []
adj_list = {}

def add_node(node):
  if node not in game_list:
    game_list.append(node)

def add_edge(node1, node2):
    temp = []
 
    if node1 in game_list:
        if node1 not in adj_list:
            temp.append(node2)
            adj_list[node1] = temp
   
        elif node1 in adj_list:
            temp.extend(adj_list[node1])
            temp.append(node2)
            adj_list[node1] = temp  

def graph():
  for node in adj_list:
    print(node, " ---> ", [i for i in adj_list[node]])

def create_graph():
    f = open('data.json')
    data = json.load(f)
    f.close()

    for i in range(len(data['name'])):
        genreA = set(data['genre'][i].split(","))
        add_node(data['name'][i])
        for j in range(len(data['name'])):
            if i != j:
                genreB = set(data['genre'][j].split(","))
                
                if genreA & genreB:
                
                    add_edge(data['name'][i], [data['name'][j], list(genreA & genreB), data['score'][j]])
       
create_graph()
with open('recommend_graph.json', 'w', encoding='utf-8') as f:
    json.dump(adj_list, f, ensure_ascii=False, indent=4)