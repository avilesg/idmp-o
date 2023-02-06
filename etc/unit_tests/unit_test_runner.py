import argparse
import json
import sys

import yaml
from rdflib import Graph


def get_unit_tests_config(unit_test_config_file_path: str) -> dict:
    with open(unit_test_config_file_path) as file:
        config = yaml.safe_load(file)
        file.close()
    return config


def get_sparql_query(config: dict) -> str:
    with open(config['sparql_template_url']) as file:
        sparql_template = file.read()
        sparql_parameters = config['parameters']
        file.close()
    sparql_query = sparql_template
    for sparql_parameter in sparql_parameters:
        sparql_query = sparql_query.replace(sparql_parameter, '"' + config['parameters'][sparql_parameter] + '"')
    return sparql_query
    

def run_unit_test(ontology_location: str, unit_test_config_file_path: str) -> bool:
    cq_tests_passed = True
    ontology = Graph()
    ontology.parse(ontology_location)
    unit_tests_config = get_unit_tests_config(unit_test_config_file_path)
    for unit_test_config in unit_tests_config.values():
        sparql_query = get_sparql_query(config=unit_test_config)
        query_result = ontology.query(sparql_query)
        query_result_as_dict = json.loads(query_result.serialize(format='json').decode())
        with open(unit_test_config['expected_output_url']) as file:
            expected_query_result = json.loads(file.read())
        if not query_result_as_dict == expected_query_result:
            print('Competency question', unit_test_config['sparql_template_url'], ' run a unit test failed.')
            cq_tests_passed = False
    return cq_tests_passed


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run unit tests')
    parser.add_argument('--ontology_location', help='Path to ontology location')
    args = parser.parse_args()
    
    cq_tests_passed = \
        run_unit_test(ontology_location=args.ontology_location, unit_test_config_file_path='/configs/unit_tests_config.yaml')
    
    if cq_tests_passed:
        sys.exit(0)
    sys.exit(-1)

