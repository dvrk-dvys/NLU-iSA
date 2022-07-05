import pandas as pd
import re
import csv
import networkx as nx
from datetime import datetime
import dateparser
from csv import writer


def append_nodes_csv(file_name, list_of_elem):
    fileVariable = open(file_name, 'r+')
    fileVariable.truncate(0)
    fileVariable.close()

    # Open file in append mode
    with open(file_name, 'a+', newline='') as write_obj:
        # Create a writer object from csv module
        csv_writer = writer(write_obj)
        csv_writer.writerow(['Id','Label'])

        for each in list_of_elem:
            if isinstance(each[0],int) is True:
                csv_writer.writerow(each)
                # print(each)
            else:
                # Add contents of list as last row in the csv file
                csv_writer.writerow([each[0].replace('"',''), each[0].replace('"','')])

def append_edges_csv(file_name, list_of_elem):
    fileVariable = open(file_name, 'r+')
    fileVariable.truncate(0)
    fileVariable.close()
    # Open file in append mode
    with open(file_name, 'a+', newline='') as write_obj:
        # Create a writer object from csv module
        csv_writer = writer(write_obj)
        csv_writer.writerow(['Source','Target','Timestamp','Weight'])

        for each in list_of_elem:
            # Add contents of list as last row in the csv file
            csv_writer.writerow(each)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    # Create Graph from .csv ___________________________________

    analysis_start_date = '2021-01-01'
    file_name = "Joe_Biden"
    # file_name = "Meghan,_Duchess_of_Sussex"
    # file_name = "Donald_Trump"
    # file_name = "Lil_Nas_X"

    G = nx.Graph()
    read_file = open(
        "/Users/jordanharris/PycharmProjects/pythonProject/upf/Data Driven Social Analytics/Data/" + file_name + ".csv",
        "r")

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    analysis_start_date = '2021-01-01'
    topic = 'Donald_Trump'

    Lines = read_file.readlines()

    index = 0
    # Strips the newline character
    for line in Lines:
        x = line.replace('\n', '').split(';')
        Lines[index] = x
        break

    for line in Lines:
        if index == 0:
            index += 1
            continue

        x = line.replace('\n', '').split(';')

        spot = 0

        # Individual Pages
        for each in x:
            if spot in [0, 5, 8, 9, 10, 11]:
                x[spot] = str(each)
                spot += 1
            elif spot == 3:
                # 2018-09-15
                x[spot] = each[0:10]
                spot += 1
            else:
                x[spot] = int(each)
                spot += 1

        Lines[index] = x
        index += 1

    # 'Source', 'Target', 'Weight', 'Time'    '2021-03-18T11:53:25Z'
    edge_timestamps = []
    counter = 0
    revisionIDs = []
    for each in Lines:
        c = 0
        if len(each) != 12:
            c += 1
            print('Amt of Data Errors:', c)
            continue

        # title
        if counter == 0:
            counter += 1
            continue

        # grammar change
        if each[6] < 4:
            # grammar change
            counter += 1
            continue

        # edit done outside of time range
        if datetime.strptime(each[3], '%Y-%m-%d').date() <= datetime.strptime(analysis_start_date, '%Y-%m-%d').date():
            counter += 1
            continue

        # 'Source', 'Target', 'Weight', 'Time'
        if each[5] == 'ADDED':
            edge_timestamps.append((each[8], each[1], .5, each[3]))
            G.add_edge(each[8], each[1], weight=.5)
        elif each[5] == 'RESTORED':
            if each[6] > 8:
                if each[8] != each[10]:
                    # Your deletion is undone
                    edge_timestamps.append((each[8], each[10], 4, each[3]))
                    G.add_edge(each[8], each[10], weight=4)
                if each[8] != each[11] and each[11] != '""':
                    # your content is restored
                    edge_timestamps.append((each[8], each[11], 1, each[3]))
                    G.add_edge(each[8], each[11], weight=1)
        elif each[5] == 'DELETED':
            if each[6] > 8:
                if each[8] != each[10]:
                    edge_timestamps.append((each[8], each[10], 8, each[3]))
                    # Your post is deleted, worst thing
                    G.add_edge(each[8], each[10], weight=8)
                if each[8] != each[11] and each[11] != '""':
                    # Your deletion is redone after it was undone
                    edge_timestamps.append((each[8], each[11], 2, each[3]))
                    G.add_edge(each[8], each[11], weight=2)

        counter += 1


    y = sorted(nx.connected_components(G), key=len, reverse=True)
    # largest = max(nx.connected_components(G), key=len)

    # for node in list(G.nodes):
    #     if node not in largest:
    #         G.remove_node(node)

    nx.write_gexf(G, topic + "_graph.gexf")
    read_file.close()

    nodes_header = ['Id', 'Label']
    nodes_data = []

    for n in G.nodes:
        if n == '""':
            nodes_data.append([n.replace('""', 'null'), 'null'])

        else:
            nodes_data.append([n, n])

    open(topic + '_nodes.csv', 'w')
    append_nodes_csv(topic + '_nodes.csv', nodes_data)

    edges_header = ['Source', 'Target', 'Weight', 'Timestamp']
    edges_data = []

    for e in set(edge_timestamps):
        process = []

        if isinstance(e[0], int) is True:
            process.append(e[0])
        elif e[0] == '""':
            process.append(e[0].replace('""', 'null'))
        else:
            process.append(e[0].replace('"',''))


        if isinstance(e[1], int) is True:
            process.append(e[1])
        elif e[1] == '""':
            process.append(e[1].replace('""', 'null'))
        else:
            process.append(e[1].replace('"', ''))

        process.append(e[3])
        process.append(e[2])

        edges_data.append(process)

    open(topic + '_edges.csv', 'w')
    append_edges_csv(topic + '_edges.csv', edges_data)

