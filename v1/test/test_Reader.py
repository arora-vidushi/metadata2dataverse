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

        self.assertEqual(["2019-04-04","none","none"], source_key_value.get("dates.date"))
        self.assertEqual(["Selent", "none", "Schembera"], source_key_value.get("creator.name"))
        self.assertEqual(["Björn", "none", "Björn"], source_key_value.get("creator.givenName"))
        self.assertEqual(["IAG","none","IMS"], source_key_value.get("creator.affiliation.name"))
        self.assertNotEqual(["German", "English"], source_key_value.get("subjects.subject.lang"))

    def convert_keys_to_numbers(self,dictionary):
        """
        Converts the keys of a dictionary to numbers recursively.
        """
        if isinstance(dictionary, dict):
            return {int(key) if key.isnumeric() else key: self.convert_keys_to_numbers(value) for key, value in dictionary.items()}
        elif isinstance(dictionary, list):
            return [self.convert_keys_to_numbers(item) for item in dictionary]
        else:
            return dictionary

    def test_JsonLdReader(self):
        sample_keys = [
            "m4i:ProcessingStep[*]",
            "m4i:ProcessingStep#obo:RO_0002234",
            "m4i:hasEmployedTool",
            "m4i:Tool",
            "m4i:Tool#rdfs:label",
            "m4i:hasEmployedTool#rdfs:label",
        ]
        expected_dict = {
            'm4i:ProcessingStep': [
                {
                    'local:measurement_0001': [
                        {'obo:RO_0002234': 'local:raw_data'}
                    ],
                    'local:temp_measurement_0001': [
                        {'obo:RO_0002234': 'local:temperature_data'}
                    ],
                    'local:pressure_measurement_0001': [
                        {'obo:RO_0002234': 'local:pressure_data'}
                    ],
                    'local:analysis_0001': [
                        {'obo:RO_0002234': 'local:analysed_data'}
                    ]
                }
            ],
            'm4i:Tool': [
                {
                    'local:hardware_assembly': [
                        {'rdfs:label': 'Hardware Assembly'}
                    ],
                    'local:temperature_sensor': [
                        {'rdfs:label': 'temperature sensor'}
                    ],
                    'local:pressure_sensor': [
                        {'rdfs:label': 'pressure sensor'}
                    ]
                }
            ],
            'm4i:hasEmployedTool': [{}]
        }
        path = './input/test.jsonld'
        test_input = open(path,'r')
        jsonld_reader= ReaderFactory.create_reader('application/jsonld')
        # jsonldapp = create_app()
        # jsonldapp.testing = True
        # jsonldcontext = jsonldapp.app_context()
        # with jsonldcontext:
        #     read_all_scheme_files()
        #     mapping_file = open('../resources/config/m4i.yml')
        #     self.jsonldmapping = read_config(mapping_file)
        #     mapping_file.close()
        # sample_keys=self.jsonldmapping
        source_key_value=jsonld_reader.read(test_input,sample_keys)
        # Check each value of the actual and expected dictionaries using assertEqual()
        for key, expected_value in expected_dict.items():
            actual_value = source_key_value.get(key)
            self.assertEqual(actual_value, expected_value)
            for i, item in enumerate(actual_value):
                self.assertEqual(item, expected_value[i])

            # Check individual values of the actual dictionary using assert statements
        self.assertEqual(source_key_value['m4i:ProcessingStep'][0]['local:measurement_0001'][0]['obo:RO_0002234'], 'local:raw_data')
        self.assertEqual(source_key_value['m4i:ProcessingStep'][0]['local:temp_measurement_0001'][0]['obo:RO_0002234'], 'local:temperature_data')
        self.assertEqual(source_key_value['m4i:ProcessingStep'][0]['local:pressure_measurement_0001'][0]['obo:RO_0002234'], 'local:pressure_data')
        self.assertEqual(source_key_value['m4i:ProcessingStep'][0]['local:analysis_0001'][0]['obo:RO_0002234'], 'local:analysed_data')
        self.assertEqual(source_key_value['m4i:Tool'][0]['local:hardware_assembly'][0]['rdfs:label'], 'Hardware Assembly')
        self.assertEqual(source_key_value['m4i:Tool'][0]['local:temperature_sensor'][0]['rdfs:label'], 'temperature sensor')
        self.assertEqual(source_key_value['m4i:Tool'][0]['local:pressure_sensor'][0]['rdfs:label'], 'pressure sensor')
        self.assertEqual(source_key_value['m4i:hasEmployedTool'], [{}])

        print(source_key_value)

        for key in sample_keys:
            if "[*]" in key:
                key = key.replace("[*]", "")
                immediate_child = {
                k for k, v in source_key_value[key][0].items()
                if isinstance(v, list) and any(isinstance(item, dict) for item in v)
                }
                print(key, " : ", immediate_child)
            if "#" in key:
                parent, child = key.split("#")
                immediate_child_keys = {
                k:v for k, v in source_key_value[parent][0].items()
                if isinstance(v, list) and any(isinstance(item, dict) for item in v)
                }

                # Get the value for the child

                values = [child_dict[child] for child_key in immediate_child_keys
                          for child_dict in [source_key_value[parent][0][child_key][0]]
                          if child in child_dict]

                print(parent, ":", child, " : ", values)

        #print(immediate_child)
        #print(source_key_value['m4i:ProcessingStep'][0])
        #actual_dict = self.convert_keys_to_numbers(source_key_value)
        #print(actual_dict)
        # Check individual values of the actual dictionary using assert statements
        # assert actual_dict[1][1][1]['obo:RO_0002234'] == 'local:raw_data'
        # assert actual_dict[1][2][1]['obo:RO_0002234'] == 'local:temperature_data'
        # assert actual_dict[1][3][1]['obo:RO_0002234'] == 'local:pressure_data'
        # assert actual_dict[1][4][1]['obo:RO_0002234'] == 'local:analysed_data'
        # assert actual_dict[2][1][1]['rdfs:label'] == 'Hardware Assembly'
        # assert actual_dict[2][2][1]['rdfs:label'] == 'temperature sensor'
        # assert actual_dict[2][3][1]['rdfs:label'] == 'pressure sensor'
        # assert actual_dict[3] == [{}]

        #print(source_key_value['m4i:Tool'][0][0][0]['rdfs:label'] )