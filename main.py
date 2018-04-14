import elasticsearch
import json
import os.path
from config import JSON_DIRECTORY
from config import QUERIES_DOCTYPE, CHART_DOCTYPE, HEDIS_INDEX_NAME
from aba_filter import aba_MLP
from cdc_filter import cdc_a1c_MLP
file_name = "sample.json"

with open(os.path.join(JSON_DIRECTORY,file_name)) as json_file:
    section_input = json.load(json_file)

#  OR

#==============================================================================
# section_input = {"DOC": """
# "VITAL SIGNS || xxxc x xxx   . HEIGHT || xxxc x xxz  .  Time ft in cm Last Measured Height Position % Measured By 
# || )))@)))@ 8:05 AM 5  . 0 6  . 00 167  . 64 02/24/2016 Standing Alejandra Collazo || xxxc x xxe  .  WEIGHT/BSA/BMI
#  || xxxc x xxf  .  Time Ib oz kg CARTER,BENJAMIN Context % BMI HgbA1c > 9.0"""
#                  }
# 
#==============================================================================

percolator_query = {
    "size": 999,
    "query": {
        "percolate": {
            "field": "query",
            "document_type": CHART_DOCTYPE,
            'document': {"DOC": section_input['DOC']},
        }
    },
    'highlight': {
        'pre_tags': ['~~'],
        'post_tags': ['~~'],
        'fields': {
            "DOC": {
                'type': 'plain',
                'fragment_size': 150,
                'number_of_fragments': 0  
            }
        }
    }
}

ES = elasticsearch.Elasticsearch(timeout=500)
res = ES.search(index=HEDIS_INDEX_NAME, doc_type=QUERIES_DOCTYPE, body=percolator_query)
#print(res)
if len(res['hits']['hits']) > 0:
    for hit in res['hits']['hits']:
        highlight_string = json.dumps(hit['highlight'])
        highlight_string = highlight_string.split('~')[0][-100 :] + " " + hit['_source']['searchTerm'] + " " + highlight_string.split('~')[-1][:100]
        searchTerm = hit['_source']['searchTerm']
        print("Search Term--> ",searchTerm)
#        print("score--> ",hit['_score']," ","Search Term--> ",searchTerm)
#        print(" Section--> ",hit['_source']['highlight']['fields'])
#        check = aba_MLP(highlight_string)
#        print("ABA check results--> ", check)
        check = cdc_a1c7_MLP(searchTerm, highlight_string)