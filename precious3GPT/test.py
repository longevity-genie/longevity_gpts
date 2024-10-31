import requests
import json
import time

API_URL = "https://cu2s6lgb4jew3tht.us-east-1.aws.endpoints.huggingface.cloud"
headers = {
    "Accept" : "application/json",
    "Authorization": "Bearer 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",
    "Content-Type": "application/json"
}

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

# with open('./generation-configs/meta2diff.json', 'r') as f:
#     config_data = json.load(f)

tissue_options = ['skin', 'muscle', 'whole blood', 'epithelium', 'artery', 'fat tissue', 'brain', 'liver']
domain_options = ['methylation', 'proteomics', 'expression']

config_data = {'instruction': ['age_group2diff2age_group'],
          # This is a chemical screening experiment in a particular age group,
          # so you'll need to use 2 intructions
          'tissue': 'whole body', # 'lung',
          'age': 70,
          'cell': '',
          'efo': '',#'EFO_0000768', #pulmonary fibrosis
          'datatype': ['methylation', 'proteomics', 'expression'] , # we want to get DEGs
          'drug': '', # 'curcumin',
          'dose': '',
          'time': '',
          'case': '',#['70.0-80.0', '80.0-90.0'], # define the age groups of interest
          'control': '', # left blank since no healthy controls participate in this experiment
          'dataset_type': '',
          'gender': '', # 'm',
          'species': 'human',
          'up': [], # left blank to be filled in by P3GPT
          'down': []
        }

# prepare request configuration
request_config = {"inputs": config_data, "mode": "meta2diff", "parameters": {
    "temperature": 0.8,
    "top_p": 0.2,
    "top_k": 3550,
    "n_next_tokens": 50,
    "random_seed": 137
}}
t = time.time()
output = query(request_config)
print("time:", time.time() - t)

print(f"Output: {str(output)}")
