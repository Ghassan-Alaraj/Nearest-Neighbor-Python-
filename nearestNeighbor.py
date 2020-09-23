import numpy as np
import networkx as nx
from matplotlib import pyplot as plt
import csv


def read_network(filename):
    """ Reads in a file to a netowrkx.Graph object

    Parameters
    ----------
    filename : str
        Path to the file to read. File should be in graphml format

    Returns
    -------
    network : networkx.Graph
        representation of the file as a graph/network

    """

    network = nx.read_graphml(filename)
    # relabel all integer nodes if possible
    def relabeller(x):
        try:
            return int(x)
        except ValueError:
            return x
    nx.relabel_nodes(network, relabeller, copy=False)
    return network

def get_rest_homes(filename):
    """ Reads in the list of rest home names

    Parameters
    ----------
    filename : str
        Path to the file to read

    Returns
    -------
    rest_homes : list of strings
        list of all rest homes
    """

    rest_homes = []
    with open(filename, 'r') as fp:
        for line in fp:
            rest_homes.append(line.strip())
    return rest_homes

def plot_path(network, path, save=None):
    """ Plots a given path of the Auckland network

    Parameters
    ----------
    network : networkx.Graph
        The graph that contains the node and edge information
    path : list
        A list of node names
    save: str or None
        If a string is provided, then saves the figure to the path given by the string
        If None, then displays the figure to the screen
    """
    lats = [network.nodes[p]['lat'] for p in path]
    lngs = [network.nodes[p]['lng'] for p in path]
    plt.figure(figsize=(8,6))
    ext = [174.48866, 175.001869, -37.09336, -36.69258]
    plt.imshow(plt.imread("akl_zoom.png"), extent=ext)
    plt.plot(lngs, lats, 'r.-')
    if save:
        plt.savefig(save, dpi=300)
    else:
        plt.show()

def save_data(name,data):
    """ save data as a txt file

    Parameters
    ----------
    name : string
        name of the file
    
    data : list
        data to be stored

    Returns
    -------

    Notes
    -----
    name should NOT include ".txt" at the end
    """ 
    #write to a file with the specified name and add .txt to string
    f=open(name + ".txt",'w')

    for p in data:
        f.write(str(p) + '\n')

    f.close()

def load_data(name):
    """ load data from a txt file

    Parameters
    ----------
    name : string
        name of the file

    Returns
    -------
    data : list
        loaded data 

    Notes
    -----
    name should NOT include ".txt" at the end
    """ 
    #write to a file with the specified name and add .txt to string
    with open(name + ".txt") as f:
        #initialize empty array
        data = []
        #initialize arbitrary value for ln
        ln = 0
        #read lines in file until all lines are read and record that information
        while ln != '':
            ln = f.readline().strip()
            data.append(ln)
        
    
    return data

def shortest_path_length(network, a, b, distance = True):
    """ find shorest distance/path between two nodes

    Parameters
    ----------
    network : networkx.Graph
        representation of the file as a graph/network
    
    a : string
        name of 'from' node
    
    b : string
        name of 'to' node
   
    distance : bool
        whether to return distance or path

    Returns
    -------
    dist : float
        shorest distance between the two nodes
    path : list
        list of nodes taken for shorest path

    Notes
    -----
    distance is defulted to True, i.e. min distance is returned by defult.
    """  

    if distance:
        return nx.shortest_path_length(network,a,b,weight = 'weight')
    elif not distance:
        return nx.shortest_path(network,a,b,weight = 'weight')
    #if distance is not valid return nothing
    return None
    

    
            
def nearest_neighbor(network,homes):
    """ A tour is construced using the nearest neighbor algorithm

    Parameters
    ----------
    network : networkx.Graph
        representation of the file as a graph/network
    
    homes : list
        names of homes that should be included in the tour

    Returns
    -------
    dist_min : list
        list of shortest distances between a pair of nodes
    path_homes_full : list
        list of homes and bus-stops taken in oreder, that were taken for shorest tour.
    path_homes : list
        list of homes taken in oreder, that were taken for shorest tour.    

    Notes
    -----
    """  
    #initialize empty lists
    dist_min = []
    path_homes = []
    path_homes_full = []

    #initialize the current node, which will always be auckland airport
    #and remove it from the list
    curr_node = homes[0]
    homes.remove(curr_node)

    #save the starting node to append at the end
    auk_airpot = curr_node

    #initialize a bool to indicate when to return to starting node
    going_back = False

    #loop while not all homes have been visited
    while not homes == []:
        #initialize empty list that will contain all the distance from current node to all
        #other nodes in the homes list
        all_dist = []

        #get all distances by finding the distance from the current node to the every other node in the region
        #that has not been vistited yet.
        for i in range(len(homes)):
            all_dist.append(shortest_path_length(network, curr_node, homes[i], distance = True))
        
        #find index of min distance, this will correspond to the index of the city
        min_index = np.argmin(all_dist)

        #record the information of nearest city
        #distance
        dist_min.append(all_dist[min_index])
        #home, for text file output 
        path_homes.append(curr_node)
        #path, for path plot that contains all bus-stops
        if len(homes) != 1:
            #if we are not returning then remove the end node as it will included as the first node in the next cycle
            path_homes_full.append(shortest_path_length(network, curr_node, homes[min_index], distance = False)[0:-1])
        else:
            #if this is the last cycle then record that node.
            path_homes_full.append(shortest_path_length(network, curr_node, homes[min_index], distance = False))

        #update current node, with the city with min distance
        curr_node = homes[min_index] 

        
        #if the last node has been visited then add the starting point to complete the tour.
        if going_back == False and len(homes) == 1:
            going_back = True
            homes.append('Auckland Airport')  
        
        #remove the current node from the list as it has been visited
        homes.remove(curr_node)

    #append auckland airport since the tour always returns to that node
    path_homes.append(auk_airpot)

    return dist_min, path_homes, path_homes_full  


def solve_region(network,region,region_name,save_distance = False):
    """ A tour is construced using the nearest neighbor algorithm

    Parameters
    ----------
    network : networkx.Graph
        representation of the file as a graph/network
    
    region : list
        names of homes that should be included in the tour
    
    region_name : string
        name of the region

    save_distance : bool
        a bool variable that determines if distances should be saved
    Returns
    -------
    None

    Notes
    -----
    This function finds the shortest tour for the specified region and saves the results in two parts:
        1.) distances_'region_name'.txt contains the distances of each 'step' taken i.e. between each home.
        2.) path_'region_name'.txt contains the path taken, only home names.
        3.) path_'region_name'.png is an image of exact path taken i.e. home names and bus-stops.
    
    save_distance is defulted to false
    """  
    #find distances and path of shortest tour.
    region_dists, region_path, region_path_full = nearest_neighbor(network,region)
    
    # change from list of lists to list i.e. flatten the 2-D list to 1-D
    flat_region_path_full = [item for sublist in region_path_full for item in sublist]

    #save data
    #note distances are recorded for optimazation purposes
    if save_distance:
        save_data("distances_"+ region_name, region_dists)


    print(sum(region_dists))
    save_data("path_" + region_name,region_path)

    #generate png
    plot_path(network,flat_region_path_full,"path_" + region_name + ".png")




def main():

    #------Import homes and region data and parition criteria------#

    #a csv file with rest homes and region was made.
    #where the header has 3 columns "house, suburb, region"
    #The subrub for each home was found using google maps, then each suburb was 
    #put into one of four regions, based on geographical location:
    #   1.) Auckland Isthmus
    #   2.) North Shore
    #   3.) South Auckland
    #   4.) West Auckland

    #import data
    #initialize empty lists
    region = []
    rest_homes = []
    #read all data and place into a list
    data = np.genfromtxt('data_region.csv', delimiter= ',', skip_header= True, dtype= str)
    #loop through list and append data into lists
    for row in data:
        region.append(row[2])
        rest_homes.append(row[0])
    

    #The data is ordered so we can split it without conditions.
    #note auckland airport is added to all regions, as it is a starting point.
    auk_airport = ['Auckland Airport']
    n = len(region)

    #Auckland Isthmus region
    search = 'Auckland Isthmus'
    AI = auk_airport + rest_homes[region.index(search) : n - region[::-1].index(search)]

    #North shore region
    search = 'North Shore'
    NS = auk_airport + rest_homes[region.index(search) : n - region[::-1].index(search)]

    #South Auckland region
    search = 'South Auckland'
    SA = auk_airport + rest_homes[region.index(search) : n - region[::-1].index(search)]

    #West auckland region
    search = 'West Auckland'
    WA = auk_airport + rest_homes[region.index(search) : n - region[::-1].index(search)]


    #---------------Construct Tours for each region and save data---------------#

    #load graph data
    auckland = read_network('network.graphml')


    #create tour for each region and save data as described in function documentation
    solve_region(auckland,AI,"1",save_distance= False)
    solve_region(auckland,NS,"2",save_distance= False)
    solve_region(auckland,SA,"3",save_distance= False)
    solve_region(auckland,WA,"4",save_distance= False)


if __name__ == "__main__":
    #Author: Ghassan Al-A'raj
    #please ensure the following files are in the same directory as the project_code.py
    #   1.) network.graphml
    #   2.) data_region.csv
    main()
   