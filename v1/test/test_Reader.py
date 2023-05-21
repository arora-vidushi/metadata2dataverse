import unittest
import sys
import json
sys.path.append('..')
from models.ReaderFactory import ReaderFactory
from api.resources import read_config, read_all_scheme_files
from api.globals import MAPPINGS,DV_FIELD, DV_CHILDREN, DV_MB
from api.app import create_app


class TestReader(unittest.TestCase):
    def setUp(self):
        self.reader = ReaderFactory.create_reader('plain/txt')
        self.app = create_app()
        self.app.testing = True
        self.context = self.app.app_context()
        with self.context:
            read_all_scheme_files()
            mapping_file = open('./resources/config/harvester.yml')
            self.mapping = read_config(mapping_file)
            mapping_file.close()

    def test_TextReader(self):
        path = './input/test_text_reader.txt'
        test_input = open(path, encoding="utf-8")
        input = test_input.read()
        test_input.close()

        with self.context:
            source_key_value = self.reader.read(
                input,
                self.mapping)
        print(source_key_value)
        self.assertEqual(["2019-04-04","none","none"], source_key_value.get("dates.date"))
        self.assertEqual(["Selent", "none", "Schembera"], source_key_value.get("creator.name"))
        self.assertEqual(["Björn", "none", "Björn"], source_key_value.get("creator.givenName"))
        self.assertEqual(["IAG","none","IMS"], source_key_value.get("creator.affiliation.name"))
        self.assertNotEqual(["German", "English"], source_key_value.get("subjects.subject.lang"))



    def test_JsonLdReader(self):
        # sample_keys = [
        #     "m4i:ProcessingStep[*]",
        #     "m4i:ProcessingStep#obo:RO_0002234",
        #     "m4i:hasEmployedTool",
        #     "m4i:Tool",
        #     "m4i:Tool#rdfs:label",
        #     "m4i:hasEmployedTool#rdfs:label",
        # ]
        sample_keys=[]
        expected_dict= {'m4i:ProcessingStep': [['local:measurement_0001'], ['local:temp_measurement_0001'], ['local:pressure_measurement_0001'], ['local:analysis_0001']], 'm4i:ProcessingStep#obo:RO_0002234': [['local:raw_data'], ['local:temperature_data'], ['local:pressure_data'], ['local:analysed_data']], 'm4i:hasEmployedTool': [], 'm4i:Tool': [['local:hardware_assembly'], ['local:temperature_sensor'], ['local:pressure_sensor']], 'm4i:ProcessingStep#m4i:Tool#rdfs:label': [['Hardware Assembly'], ['temperature sensor'], ['pressure sensor']], 'm4i:ProcessingStep#m4i:hasEmployedTool': [['local:hardware_assembly'], ['local:temperature_sensor'], ['local:pressure_sensor'], ['none']], 'm4i:ProcessingStep#m4i:realizesMethod#rdfs:label': [], 'm4i:ProcessingStep#obo:RO_0000057': [['local:alex'], ['none'], ['none'], ['local:doris']], 'm4i:ProcessingStep#schema:startTime': [['2022-03-01T09:03:01'], ['2022-03-01T09:03:01'], ['2022-03-10T13:35:11'], ['2022-03-14T09:15:00']]}

        path = './input/test.jsonld'
        test_input = open(path,'r')
        jsonld_reader= ReaderFactory.create_reader('application/jsonld')
        jsonldapp = create_app()
        jsonldapp.testing = True
        jsonldcontext = jsonldapp.app_context()
        with jsonldcontext:
            read_all_scheme_files()
            mapping_file = open('../resources/config/m4i.yml')
            self.jsonldmapping = read_config(mapping_file)
            mapping_file.close()
        # print(sample_keys)
        source_key_value=jsonld_reader.read(test_input,self.jsonldmapping)
        #print(source_key_value)
        #Check each value of the actual and expected dictionaries using assertEqual()
        for key, expected_value in expected_dict.items():
            actual_value = source_key_value.get(key)
            self.assertEqual(actual_value, expected_value)
            for i, item in enumerate(actual_value):
                self.assertEqual(item, expected_value[i])


        list_of_source_keys = self.jsonldmapping.get_source_keys()
        list_of_source_keys = list(dict.fromkeys(list_of_source_keys))
        #print(list_of_source_keys)
        # for key in list_of_source_keys:
            # if "[*]" in key:
                # key = key.replace("[*]", "")
                # immediate_child = {
                # k for k, v in source_key_value[key][0].items()
                # if isinstance(v, list) and any(isinstance(item, dict) for item in v)
                # }
                # immediate_child=source_key_value[key]
                # immediate_child= {k for k}
                # print(key, " : ", immediate_child)
            # if "#" in key:
                # parent, child = key.split("#")
                # value = self.get_nested_dict_values(source_key_value, child, parent)
                # print(parent, ":" , child, ":", value, "\n \n")
                # immediate_child_keys = source_key_value[parent]

                # #Get the value for the child
                # for k in immediate_child_keys:

                #     if isinstance(k, dict):
                #         immediate_child = {
                #             v for p, v in k.items()
                #             if isinstance(v, list) and any(isinstance(item, dict) for item in v)
                #             }
                #         print(immediate_child)
                        # if child in k.keys():
                        #     print(k[child])
            #     values = [child_dict[child] for child_key in immediate_child_keys
            #               for child_dict in [source_key_value[parent][0][child_key][0]]
            #               if child in child_dict]

                # print(parent, ":", child, " : ", values)

        #print(immediate_child)
        #print(source_key_value['m4i:ProcessingStep'][0])
        #actual_dict = self.convert_keys_to_numbers(source_key_value)
        #print(actual_dict)
        #print(source_key_value['m4i:Tool'][0][0][0]['rdfs:label'] )

