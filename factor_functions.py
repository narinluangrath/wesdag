import json
import csv
from libpgm.graphskeleton import GraphSkeleton

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
#        blah, blah, blah ... \n
#        blah, blah, blah ... \n
#        moar, moar, moar ... \n
#        etc...
# output:
#       (['blah', 'blah', 'blah', ...],
#        ['blah', 'blah', 'blah', ...])
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

# O(n), n = |xs|
def times(xs):
    product = 1
    for x in xs:
        product = product * x
    return product

# O(n)
def skip_n_lines(reader_file, n):
    for i in range(n):
        reader_file.next()

# O(n), n = # of edges
def get_neighbors(wesdagssfile, vertex):
    (vert_list, edge_list) = top_two_rows(wesdagssfile)
    parsed_edges = parse_edges(filter_empty(edge_list[1:]))
    neighbors = [vertex]
    for [v1, v2] in parsed_edges:
        if (v2 == vertex):
            neighbors.append(v1)
    return neighbors

# O(n), n = # of vertices
# double check ^^...
def state_space(wesdagssfile):
    ss_dict = {}
    open_wesdagss = open(wesdagssfile, 'rU')
    data_wesdagss = csv.reader(open_wesdagss, delimiter=',')
    skip_n_lines(data_wesdagss, 4)
    for row in data_wesdagss:
        filt_row = filter_empty(row)
        if (filt_row != []):
            ss_dict[filt_row[0]] = filt_row[1:]
    return ss_dict

# O(n), n = |vert_list|^2
def calculate_w(wesdagssfile, vert_list):
    ss = state_space(wesdagssfile)
    w_dict = {}
    i = 0
    while i < len(vert_list):
        w_dict[vert_list[i]] = times([ int(ss[vert][0]) for vert in vert_list[(i+1):] ])
        i = i + 1
    return w_dict

# O(n), n = |vert_list|^2
def calculate_mult(wesdagssfile, vert_list):
    ss = state_space(wesdagssfile)
    mult_dict = {}
    i = 0
    while i < len(vert_list):
        mult_dict[vert_list[i]] = times([ int(ss[vert][0]) for vert in vert_list[:i]])
        i = i + 1
    return mult_dict

# O(n * m), n = # rows, m = # columns
def transpose(matrix):
    return [list(i) for i in zip(*matrix)]

# O(?)
def make_factor_template(wesdagssfile, vertex, outputfilename):
    if wesdagss_precond(wesdagssfile):
        neighbors = get_neighbors(wesdagssfile, vertex) # O( edges )
        w = calculate_w(wesdagssfile, neighbors) # O( vert_list ^2 )
        mult = calculate_mult(wesdagssfile, neighbors)
        template = []
        for vert in neighbors: # O( neighbors * max number of states of all neighbors)
            w_times = []
            for state in state_space(wesdagssfile)[vert][1:]:
                w_times = w_times + ([state]*(w[vert])) # constant time ?
            template.append(w_times*mult[vert])
        template = transpose(template) # O( state space * neighbors) ?
        open_template = open(outputfilename + '.xlsx', 'wb')
        data_template = csv.writer(open_template, delimiter=',')
        data_template.writerow(neighbors + ['Probability'])
        for row in template:
            data_template.writerow(row)
