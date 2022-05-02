
import operator
import matplotlib.pyplot as plt
import math
import json

def construct_node(val, left, right):
    """
    Node constructor in json format
    """
    node = {}
    node["val"] = val
    node["left"] = left
    node["right"] = right
    return node

def build_kd_tree(res_list, depth):
    """
    Construct the k-d tree from a list of restaurants
    Return a dict of kd-tree
    """
    if len(res_list) == 0:
        return "None"
    
    res_list.sort(key=operator.itemgetter(depth % 2))
    middle = len(res_list) // 2

    return construct_node(
        val = res_list[middle],
        left = build_kd_tree(res_list[:middle], depth+1),
        right = build_kd_tree(res_list[middle+1:], depth+1)
    )

def show_tree(tree, plot=True):
    """
    Data visualization of the kd-tree partition
    """
    def recur_p(node, depth):
        if node == "None":
            return
        if depth % 2 == 0:
            plt.axvline(x=node["val"][0], ymin=0, ymax=1)
        else:
            plt.axhline(y=node["val"][1], xmin=0, xmax=5)
        plt.scatter(node["val"][0], node["val"][1])
        plt.text(node["val"][0], node["val"][1], f'({node["val"][0]}, {node["val"][1]})')
        recur_p(node["left"], depth+1)
        recur_p(node["right"], depth+1)

    recur_p(tree, 0)
    if plot:
        plt.xlabel("Latitude")
        plt.ylabel("Longitude")      
        plt.show()

def nodes_within_distance(tree, x, y, d):
    """
    Search the kd tree to find node within distance d from location (x, y)
    return: a list of nodes that satisfy the condition 
    """
    node_list = []
    def recur_h(node, x, y, d, depth):
        if node == "None":
            return

        if within_distance(x, y, node["val"][0], node["val"][1], d):
            node_list.append(node["val"])

        if depth % 2 == 0:
            # Partitioning over x
            if within_distance(x, y, node["val"][0], y, d):
                # if the partition line (vertical at x) 
                # passes through or intersects the circle, search both branches
                recur_h(node["left"], x, y, d, depth+1)
                recur_h(node["right"], x, y, d, depth+1)
            else:
                # otherwise consider which branch is closer to the target
                if x< node["val"][0]:
                    recur_h(node["left"], x, y, d, depth+1)
                else:
                    recur_h(node["right"], x, y, d, depth+1)

        else:
            #partitioning over y
            if within_distance(x, y, x, node["val"][1], d):
                # if the partition line (horizontal at y) 
                # passes through or intersects the circle, search both branches
                recur_h(node["left"], x, y, d, depth+1)
                recur_h(node["right"], x, y, d, depth+1)
            else:
                # otherwise consider which branch is closer to the target
                if y< node["val"][1]:
                    recur_h(node["left"], x, y, d, depth+1)
                else:
                    recur_h(node["right"], x, y, d, depth+1)  
    recur_h(tree, x, y ,d, 0)

    figure, axes = plt.subplots()
    show_tree(s, plot=False)
    axes.add_artist(plt.Circle((x, y), d,fill=False))
    # plt.text(x, y, f'({x}, {y})')
    plt.xlim([0, 10])
    plt.ylim([0, 10])        
    plt.show()

    return node_list

def within_distance(x1, y1, x2, y2, d):
    return (x1-x2)**2 + (y1-y2)**2 <= d**2

# def within_distance(lat1, lon1, lat2, lon2, d):
#     """ 
#     Determines whether the distance between
#     (lat1, lon1) and (lat2, lon2) is within d
#     """

#     # convert lattitude and longitude to radian
#     lat1 = lat1/(180/math.pi) 
#     lat2 = lat2/(180/math.pi) 
#     lon1 = lon1/(180/math.pi) 
#     lon2 = lon2/(180/math.pi) 

#     # radius of Earch in km
#     r = 6371
       
#     # Haversine formula
#     dlon = lon2 - lon1
#     dlat = lat2 - lat1
#     a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
#     c = 2 * math.asin(math.sqrt(a))
    
#     return (c * r)**2 <= d**2

reference_points = [ [1, 2, 0], [3, 2, 1], [4, 1, 2], [3, 5, 3] ]
s = build_kd_tree(reference_points, 0)
      


print(nodes_within_distance(s, 2.5, 1.5, 1))


## visualize the sample_kd_tree_AnnArbor.json
# file = open("sample_kd_tree_AnnArbor.json", 'r')
# tt = json.loads(file.read())
# file.close()
# show_tree(tt)