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

def filter_empty(xs):
    return [x for x in xs if ((x != []) and (x != "") and (x != [""]))]

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
        csv_row_no_empty = [e for e in csv_row if e != ""]
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
        csv_row_no_empty = [e for e in csv_row if e != ""]
        check1 = (csv_row_no_empty[0].upper() == "VERTEX")
        check2 = (len(csv_row_no_empty[1:]) == num)
        return (check1 and check2)
    except:
        return False

def vert_obs_ss_check(csv_reader_obj, num):
    try:
        csv_row = csv_reader_obj.next()
        csv_row_no_empty = [e for e in csv_row if e != ""]
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

# If cytoscapefile holds a DAG, then write cytoscape digraph to wesdag file named outputfilename.
# (If not a DAG, return error and do not write.)
# def convert_cys_to_wesdag(cytoscapefile, outputfilename)

# Instantiate (return) a graphskeleton object and load with the DAG contained in wesdagfile.
def read_wesdag_to_graphskeleton(wesdagfile):
    if wesdag_precond(wesdagfile):
        (vert_list, edge_list) = top_two_rows(wesdagfile)
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

# Instantiate (return) a graphskeleton object and load with the DAG contained in wesdagssfile (ignoring state space).
def read_wesdagss_to_graphskeleton(wesdagssfile):
    if wesdagss_precond(wesdagssfile):
        (vert_list, edge_list) = top_two_rows(wesdagssfile)
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

# Write a wesdagss_template named outputfilenameself.
def make_wesdagss_template(wesdagfile, outputfilename):
    if wesdag_precond(wesdagfile):
        open_wesdag = open(wesdagfile, 'rU')
        data_wesdag = filter_empty(csv.reader(open_wesdag, delimiter=','))
        open_template = open(outputfilename + '.xlsx', 'wb')
        data_template = csv.writer(open_template, delimiter=',')
        for row in data_wesdag:
            data_template.writerow(row)
        data_template.writerow(['VERTEX STATES'])
        data_template.writerow(['Vertex', 'num states'])
        vert_list = top_row(wesdagfile)
        for vert in (filter_empty(vert_list[1:])):
            data_template.writerow([vert])

# Write a wesdagssdata_template file named outputfilename with numcolumns for state observations.
def make_wesdagssdata_template(wesdagssfile, numcolumns, outputfilename):
    if wesdagss_precond(wesdagssfile):
        open_wesdagss = open(wesdagssfile, 'rU')
        data_wesdagss = filter_empty(csv.reader(open_wesdagss, delimiter=','))
        open_template = open(outputfilename + '.xlsx', 'wb')
        data_template = csv.writer(open_template, delimiter=',')
        for row in data_wesdagss:
            data_template.writerow(row)
        data_template.writerow(['NUM OBSERVATIONS', str(numcolumns)])
        data_template.writerow(obs_row(numcolumns))
        for vert in (filter_empty(top_row(wesdagssfile)[1:])):
            data_template.writerow([vert])

def main():
    global skel
    looping = True
    while looping:
        choice = input("\n"+
                       "1. read_wesdag_to_graphskeleton\n"+
                       "2. read_wesdagss_to_graphskeleton\n"+
                       "3. make_wesdagss_template\n"+
                       "4. make_wesdagssdata_template\n\n"+
                       "Pick a number: ")
        if (choice == 1):
            wesdag_file = raw_input("Enter wesdag file name: ")
            skel = read_wesdag_to_graphskeleton(wesdag_file)
            print "Use variable 'skel' to access graph skeleton."
        elif (choice == 2):
            wesdagss_file = raw_input("Enter wesdagss file name: ")
            skel = read_wesdagss_to_graphskeleton(wesdagss_file)
            print "Use variable 'skel' to access graph skeleton."
        elif (choice == 3):
            wesdag_file = raw_input("Enter wesdag file name: ")
            template_name = raw_input("Enter output file name: ")
            make_wesdagss_template(wesdag_file, template_name)
            print "Saved as " + template_name + ".xlsx"
        elif (choice == 4):
            wesdag_file = raw_input("Enter wesdagss file name: ")
            num_col = input("Enter number of obserations: ")
            template_name = raw_input("Enter output file name: ")
            make_wesdagssdata_template(wesdag_file, num_col, template_name)
            print "Saved as " + template_name + ".xlsx"
        else:
            print "Not a valid number.\n"
        stop = raw_input("Done? [y / n]: ")
        if (stop != "n"):
            looping = False

main()
