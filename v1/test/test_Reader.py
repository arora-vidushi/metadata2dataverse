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
        print(source_key_value)

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
        expected_dict= {'m4i:ProcessingStep': ['local:measurement_0001', 'local:temp_measurement_0001', 'local:pressure_measurement_0001', 'local:analysis_0001'], 'm4i:ProcessingStep#obo:RO_0002234': ['local:raw_data', 'local:temperature_data', 'local:pressure_data', 'local:analysed_data'], 'm4i:hasEmployedTool': [], 'm4i:Tool': ['local:hardware_assembly', 'local:temperature_sensor', 'local:pressure_sensor'], 'm4i:ProcessingStep#m4i:Tool#rdfs:label': ['Hardware Assembly', 'temperature sensor', 'pressure sensor'], 'm4i:ProcessingStep#m4i:hasEmployedTool': ['local:hardware_assembly', 'local:temperature_sensor', 'local:pressure_sensor', 'none'], 'm4i:ProcessingStep#m4i:realizesMethod#rdfs:label': [], 'm4i:ProcessingStep#obo:RO_0000057': ['local:alex', 'none', 'none', 'local:doris'], 'm4i:ProcessingStep#schema:startTime': ['2022-03-01T09:03:01', '2022-03-01T09:03:01', '2022-03-10T13:35:11', '2022-03-14T09:15:00']}

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
        # print(source_key_value)
        #Check each value of the actual and expected dictionaries using assertEqual()
        for key, expected_value in expected_dict.items():
            actual_value = source_key_value.get(key)
            self.assertEqual(actual_value, expected_value)
            for i, item in enumerate(actual_value):
                self.assertEqual(item, expected_value[i])


        list_of_source_keys = self.jsonldmapping.get_source_keys()
        list_of_source_keys = list(dict.fromkeys(list_of_source_keys))

