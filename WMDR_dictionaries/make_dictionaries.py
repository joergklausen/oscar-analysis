#### import ####

import os
import csv
import yaml
import json
import shutil


#### make dictionary  #####

def make_dictionary(label):

    # make dictionary
    reader = csv.reader(open(os.getcwd()+'/WMDR_dictionaries/'+label+'.csv', 'r'))
    dictionary = {}
    for row in reader:
        k, v = row
        dictionary[k] = v

    # save dictionary as .json file
    filename = label+"_dictionary.json"
    with open(filename, 'w') as f:
        f.write(json.dumps(dictionary))

    # move dictionary to dictionaries folder
    shutil.move(filename, os.getcwd()+'/WMDR_dictionaries/'+filename)




# variables = ['ObservedVariableAtmosphere_WMDR', 'ObservedVariableOcean_WMDR', 'ObservedVariableTerrestrial_WMDR']
variables = ["T_GO_VARIABLE_REF"]
for var in variables:
    make_dictionary(label=var)
