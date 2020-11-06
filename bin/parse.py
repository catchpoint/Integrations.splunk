'''
    Author: Catchpoint Systems, All Rights Reserved.
    Raw Data Mapping Algorithm and Implementation for Splunk-Catchpoint Integration
'''
'''
@param x:
    represents one of the five keys being sent into the function for evaluation.
@param data:
    represents the data structure (a dictionary) containing values
@elements:
    elements = ['synthetic_metrics', 'host_Ip', 'breakdown_2', 'breakdown_1', 'dimension']
overview:
    this function can be considered as the driver for performing the mapping of values
    contained within the 'detail', 'indicators', 'tracepoints' index.
'''
def init_map(data, length, blueprint, values_list, elements, indicator_length, indicator_blueprint, indicator_values_list, tracepoint_length, tracepoint_blueprint, tracepoint_values_list):
    an_item = {}
    '''
    overview: for each key (otherwise known as variable x), create a new key/value pair within the dictionary named 'an_item'
    through the process of case matching. if match is found, index into the value_collection at element x
    and return. The return value will become the 'value' field within the new key/value pair structure we are constructing.
    ### notes ###
    an_item: a mapped dictionary which resides under the parent key -- 'detail'
    an_item[x] = ...: adds a new key/value pair into the dictionary 'an_item'
    '''
    parseParametersDict = {
        "data" : data,
        "length" : length,
        "blueprint": blueprint,
        "values_list" : values_list,
        "elements" : elements,
        "indicator_length" : indicator_length,
        "indicator_blueprint" : indicator_blueprint,
        "indicator_values_list" : indicator_values_list,
        "tracepoint_length" : tracepoint_length,
        "tracepoint_blueprint" : tracepoint_blueprint,
        "tracepoint_values_list" : tracepoint_values_list
    }
    
    for x in elements:
        an_item[x] = case_match_metrics(x, parseParametersDict)
    return an_item

'''
@param length:
    represents the length of value_collection dictionary indexed at 'synthetic_metric' --
    hence, length can be described as the length of the synthetic_metric array
    note: value_collection is simply a large array filled entirely of values. more pointedly,
    value_collection contains all the values to be mapped. it is extracted from the following structure.
    {
    start : ..
    end : ..
    timezone : ..
    detail : {
            fields : blueprint located here.
            items : value_collection located here.
        }
    }
@param blueprint:
    represents a dictionary of 'key/value pairs' -- otherwise known as a dictionary of dictionaries.
    we use blueprint to index into 'synthetic_metrics' dictionary.
    blueprint['synthetic_metrics'] represents the place-holding structure (dictionary) we will use as a scaffold to build our
    desired mapping with the values held in the value_collection dictionary
    indexing in once more to the 'name' field , we use the value of blueprint['synthetic_metrics']['name'] to represent the keys
    of the synthetic_metrics dictionary within the brand new data structure we are constructing.
@param value_collection_at_synthetic_metrics_index:
    note: value_collection is an array of dictionaries, all containing the values to be mapped for the parent key 'detail'.
    value_collection['at some arbitrary array index']['synthetic_metrics'] fetches a singular synthetic_metrics array holding
    only synthetic_metrics values produced from making a get request to the Catchpoint API tests endpoint.
Logic: If we iterate through the 'value_collection_at_synthetic_metrics_index' array while, at the same time, iterating through the blueprint structure at the desired indices, we are able to perform dynamic mappings across all synthetic_metrics values.
'''
def map_synthetic(length, blueprint, value_collection_at_synthetic_metrics_index):
    synthetic_metrics_structure = {}
    for index in range(length):
        if blueprint[index]['name'] != None:
            key = blueprint[index]['name']
        else:
            key = None
        value = str(value_collection_at_synthetic_metrics_index[index])
        synthetic_metrics_structure.update({str(key): value})
    return synthetic_metrics_structure


'''
@param x:
    represents one of the three keys being sent into the function for evaluation.
@param data:
    represents the data structure (a dictionary) containing values
Logic: If we were to index into the data structure, 'data' at 'x' (data[x]),
the information fetched can then be set as the value field of a 'key/value pair' which sits within
the new data structure we are building.
'''
def case_match_main(x, data):
    return {
        'start': str(data[x]),
        'end': str(data[x]),
        'timezone': data[x]
    }.get(x, None)


'''
@param x:
    represents one of the five keys being sent into the function for evaluation.
@param data:
    represents the data structure (a dictionary) containing values
@other parameters:
    see map_synthetic function above for more information.
Logic: If we were to index into the data structure, 'data' at 'x' (data[x]),
the information fetched can then be set as a value field of 'key/value' object within a brand new data structure.
returns JSON, an array or a string value.
'''

def case_match_metrics(x, parseParametersDict):

    if x == 'synthetic_metrics':
        return {
            x: map_synthetic(parseParametersDict["length"], parseParametersDict["blueprint"], parseParametersDict["values_list"])
        }.get(x, None)
    elif x == 'indicators':
        return {
            x: map_synthetic(parseParametersDict["indicator_length"], parseParametersDict["indicator_blueprint"], parseParametersDict["indicator_values_list"])
        }.get(x, None)
    elif x == 'tracepoints':
        return {
            x: map_synthetic(parseParametersDict["tracepoint_length"], parseParametersDict["tracepoint_blueprint"], parseParametersDict["tracepoint_values_list"])
        }.get(x, None)
    else:
        return {
            x: parseParametersDict["data"][x]
        }.get(x, None)

'''
overview: sifts through the 'detail' construct, returns it's member elements when matches are made, and feeds these
values into a more manageable, compact dictionary
'''
def case_match_detail_elements(x, structure, structure_key):
    return {
        'fields': {'value_collection_blueprint': structure[structure_key][x]},

        'items': {'value_collection': structure[structure_key][x],
                  'how_many_items_in_items_array': len(structure[structure_key][x])}

    }.get(x, None)


''' overview: maps raw data values into a key/value structure
the function walks through the raw data (data structure) and executes a mapping
of fields specified by the raw data
:returns: a generator object which handles control over to the caller
'''
def search(structure):
    dictionary = {}
    details = {}
    simple_metrics = {}

    if structure is not None:
        '''
        overview: alerts handler.
        '''
        if 'alerts' in structure.keys():
          headers = {'start':structure['start'], 'end':structure['end'], \
            'page_number':structure['page_number']
          }
          
          solution = []
          value = structure 
          for k in value:
            if type(value[k]) is not list and type(value[k]) is not dict:
              headers.update({k : value[k]})
            
            else:
              for element in value[k]:
                event = {}
                event[k] = element
                event.update(headers)
                solution.append(event)
                yield event

        else:
            # overview: the algorithm begins by searching through the four main keys of the structure:
            # 'start', 'end', 'timezone' and 'details'
            for structure_key in structure:

                ''' overview: case match against the first three main fields '''
                simple_metrics[structure_key] = case_match_main(structure_key, structure)

                if structure_key == 'detail':

                    for child_structure in structure[structure_key]:

                        '''
                        overview: populate the dictionary object with a blueprint object, the count of key fields
                        for the blueprint object and the values to populate the blueprint object with.
                        Logic: To determine if case 'child_structure' is in 'detail', match against all keys in function --
                        return value field of matched. If no match found, return the None object. Do while there exist
                        remaining children of detail to iterate through.
                        Debugging note: length of items in items array computed by --
                        len(structure[structure_key][child_structure])
                        '''
                        dictionary[child_structure] = case_match_detail_elements(child_structure, structure, structure_key)
                    
                    _item_count = dictionary['items']['how_many_items_in_items_array']
                    _blueprint = dictionary['fields']['value_collection_blueprint']
                    value_collection = dictionary['items']['value_collection']

                    if _item_count and _blueprint and value_collection:

                        for i in range(_item_count):
                            index = "details_{0}".format(i)

                            # Check if indicators and tracepoints are present in the API response.
                            if value_collection[i].get('indicators') != None:
                                indicator_length = len(value_collection[i]['indicators'])
                                indicator_blueprint = _blueprint['indicators']
                                indicator_values_list = value_collection[i]['indicators']
                            else:
                                indicator_length = 0
                                indicator_blueprint = None
                                indicator_values_list = None
                            
                            if value_collection[i].get('tracepoints') != None:
                                tracepoint_length = len(value_collection[i]['tracepoints'])
                                tracepoint_blueprint = _blueprint['tracepoints']
                                tracepoint_values_list = value_collection[i]['tracepoints']
                            else:
                                tracepoint_length = 0
                                tracepoint_blueprint = None
                                tracepoint_values_list = None
                            
                            details[index] = init_map(value_collection[i],
                                                      len(value_collection[i]['synthetic_metrics']),
                                                      _blueprint['synthetic_metrics'],
                                                      value_collection[i]['synthetic_metrics'],
                                                      value_collection[i].keys(),
                                                      indicator_length,
                                                      indicator_blueprint,
                                                      indicator_values_list,
                                                      tracepoint_length,
                                                      tracepoint_blueprint,
                                                      tracepoint_values_list)
                            
                            simple_metrics.pop('detail', None)
                            simple_metrics['start'] = structure['start']
                            simple_metrics['end'] = structure['end']
                            details[index].update(simple_metrics)
                            yield details[index]
