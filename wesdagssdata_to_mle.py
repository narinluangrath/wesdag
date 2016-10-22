import json
import csv

from libpgm.nodedata import NodeData
from libpgm.graphskeleton import GraphSkeleton
from libpgm.discretebayesiannetwork import DiscreteBayesianNetwork
from libpgm.pgmlearner import PGMLearner

# global variables
skel = None


# ------------------------------------------ HELPER FUNCTIONS ----------------------------------------- #

# input ['e1->e2', 'e3->e4', ...]
# output [['e1', 'e2'], ['e3', 'e4'], ...]
def parse_edges(es):
    return [e.split("->") for e in es]

# input ['blah', '', 'blah1', '', '', 'stuff']
# output ['blah', 'blah1', 'stuff']
def filter_empty(xs):
    return [x for x in xs if (x != "")]

# input:
#        text1, text2, text3 ... \n
#        text4, text5, text6 ... \n
#        text7, text8, text9 ... \n
#        etc...
# output:
#       (['text1', 'text2', 'text3', ...],
#        ['text4', 'text5', 'text6', ...])
def top_two_rows(wesdagfile):
    open_csv = open(wesdagfile, 'rU')
    data_csv = csv.reader(open_csv, delimiter=',')
    row1 = data_csv.next()
    row2 = data_csv.next()
    return (row1, row2)

def top_row(csvfile):
    open_csv = open(csvfile, 'rU')
    data_csv = csv.reader(open_csv, delimiter=',')
    return data_csv.next()

# obs_row(n) = ['Vertex', 'obs1', 'obs2', ... , 'obsn']
def obs_row(n):
    return_me = ['Vertex']
    for i in range(1, n+1):
        return_me.append('obs' + str(i))
    return return_me

# -------- HELPER FUNCTIONS FOR VERIFYING WES FILES ARE FORMATTED RIGHT ------ #

# returns true iff file_name ends with '.csv'
def is_csv(file_name):
    try:
        return (file_name.split('.')[1] == 'csv')
    except:
        return False

def vert_set_check(csv_reader_obj):
    try:
        csv_row = csv_reader_obj.next()
        return ((csv_row[0].upper() == "VERTEX SET"), len(csv_row)-1)
    except:
        return (False, -1)

def edge_set_check(csv_reader_obj):
    try:
        csv_row = csv_reader_obj.next()
        check1 = (csv_row[0].upper() == "EDGE SET")
        check2 = True
        for edge in csv_row[1:]:
            if not (("->" in edge) or (edge == "")):
                check2 = False
        return (check1 and check2)
    except:
        return False

def vert_states_check(csv_reader_obj):
    try:
        csv_row = csv_reader_obj.next()
        return (csv_row[0].upper() == "VERTEX STATES")
    except:
        return False

def vert_num_check(csv_reader_obj):
    try:
        csv_row = csv_reader_obj.next()
        check1 = (csv_row[0].upper() == "VERTEX")
        check2 = (csv_row[1].upper() == "NUM STATES" or
                  csv_row[1].upper() == "NUM_STATES")
        return (check1 and check2)
    except:
        return False

def vert_ss_check(csv_reader_obj):
    try:
        csv_row = csv_reader_obj.next()
        num_states = int(csv_row[1])
        csv_row_no_empty = filter_empty(csv_row)
        return (len(csv_row_no_empty[2:]) == num_states)
    except:
        return False

def num_obs_check(csv_reader_obj):
    try:
        csv_row = csv_reader_obj.next()
        return ((csv_row[0].upper() == "NUM OBSERVATIONS"), int(csv_row[1]))
    except:
        return (False, -1)

def vert_obs_check(csv_reader_obj, num):
    try:
        csv_row = csv_reader_obj.next()
        csv_row_no_empty = filter_empty(csv_row)
        check1 = (csv_row_no_empty[0].upper() == "VERTEX")
        check2 = (len(csv_row_no_empty[1:]) == num)
        return (check1 and check2)
    except:
        return False

def vert_obs_ss_check(csv_reader_obj, num):
    try:
        csv_row = csv_reader_obj.next()
        csv_row_no_empty = filter_empty(csv_row)
        return (len(csv_row_no_empty[1:]) == num)
    except:
        return False

# returns true iff wesdagfile is correctly formatted, raises an error otherwise
def wesdag_precond(wesdagfile):
    if (not is_csv(wesdagfile)):
        raise NameError("Not a csv file")
    open_csv = open(wesdagfile, 'rU')
    data_csv = csv.reader(open_csv, delimiter=',')
    row = 1
    (did_pass, num_vert) = vert_set_check(data_csv)
    if (not did_pass):
        raise NameError("Error on row " + str(row))
    else:
        row += 1
    for func in [edge_set_check]:
        if (not func(data_csv)):
            raise NameError("Error on row " + str(row))
        else:
            row += 1
    return True

# returns true iff wesdagssfile is correctly formatted
def wesdagss_precond(wesdagssfile):
    if (not is_csv(wesdagssfile)):
        raise NameError("Not a csv file")
    open_csv = open(wesdagssfile, 'rU')
    data_csv = csv.reader(open_csv, delimiter=',')
    row = 1
    (did_pass, num_vert) = vert_set_check(data_csv)
    if (not did_pass):
        raise NameError("Error on row " + str(row))
    else:
        row += 1
    for func in [edge_set_check, vert_states_check, vert_num_check] + [vert_ss_check]*num_vert:
        if (not func(data_csv)):
            raise NameError("Error on row " + str(row))
        else:
            row += 1
    return True

#  returns true iff wesdatssdatafile is correctly formatted
def wesdagssdata_precond(wesdagssdatafile):
    if (not is_csv(wesdagssdatafile)):
        raise NameError("Not a csv file")
    open_csv = open(wesdagssdatafile, 'rU')
    data_csv = csv.reader(open_csv, delimiter=',')
    row = 1
    (did_pass, num_vert) = vert_set_check(data_csv)
    if (not did_pass):
        raise NameError("Error on row " + str(row))
    else:
        row += 1
    for func in [edge_set_check, vert_states_check, vert_num_check] + [vert_ss_check]*num_vert:
        if (not func(data_csv)):
            raise NameError("Error on row " + str(row))
        else:
            row += 1
    (did_pass2, num_obs) = num_obs_check(data_csv)
    if (not did_pass2):
        raise NameError("Error on row " + str(row))
    else:
        row += 1
    for func in [vert_obs_check] + [vert_obs_ss_check]*num_vert:
        if (not func(data_csv, num_obs)):
            raise NameError("Error on row " + str(row))
        else:
            row += 1
    return True

# --------------------------------------- END HELPER FUNCTIONS -------------------------------------- #


def skip_n_lines(reader_file, n):
    for i in range(n):
        reader_file.next()

def transpose(matrix):
    return [list(i) for i in zip(*matrix)]

def read_wesdagssdata_to_graphskeleton(wesdagssdatafile):
    if wesdagssdata_precond(wesdagssdatafile):
        (vert_list, edge_list) = top_two_rows(wesdagssdatafile)
        the_dict = {}
        the_dict['V'] = filter_empty(vert_list[1:])
        the_dict['E'] = filter_empty(parse_edges(edge_list[1:]))
        the_dict['Vdata'] = {} # edit this later?
        txt_temp = open('temp_pgm.txt', 'w')
        json_dump = json.dumps(the_dict, indent=4, separators=(',', ': '))
        print >> txt_temp, json_dump
        txt_temp.close()
        skel = GraphSkeleton()
        skel.load('temp_pgm.txt')
        return skel

def read_wesdagssdata_to_mle(wesdagssdatafile):
    if wesdagssdata_precond(wesdagssdatafile):
        open_wesdagssdata = open(wesdagssdatafile, 'rU')
        data_wesdagssdata = csv.reader(open_wesdagssdata, delimiter=',')
        skip_n_lines(data_wesdagssdata, 10)
        the_matrix = transpose(data_wesdagssdata)
        vert_list = the_matrix[0]
        the_list = []
        for obs in the_matrix[1:]:
            obs_dict = {}
            vert_obs = zip(vert_list, obs)
            for (vert, state) in vert_obs:
                obs_dict[vert] = state
            the_list.append(obs_dict)
        skel = read_wesdagssdata_to_graphskeleton(wesdagssdatafile)
        learner = PGMlearner()
        result = learner.discrete_mle_estimateparams(skel, the_list)
        return result
