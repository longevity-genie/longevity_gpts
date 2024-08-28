import requests

API_URL = "https://cu2s6lgb4jew3tht.us-east-1.aws.endpoints.huggingface.cloud"
headers = {
    "Accept" : "application/json",
    "Authorization": "Bearer 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",
    "Content-Type": "application/json"
}

# tissue_options = ['skin', 'muscle', 'whole blood', 'epithelium', 'artery', 'fat tissue', 'brain', 'liver']
# domain_options = ['methylation', 'proteomics', 'expression']

def get_omics_data(age:float, tissue:str = 'whole body', drug:str = '', gender:str = '', domain:str = 'expression'):
    """ This function retrieves omics data for given parameters.
     age - age in years
     tissue - is tissue name like: 'skin', 'muscle', 'whole blood', 'epithelium', 'artery', 'fat tissue', 'brain', 'liver', 'lung'
     drug - drug or biological active substance name
     gender - 'm' for male and 'f' for female
     domain - must be one of these 'methylation', 'proteomics', 'expression' """
    config_data = {'instruction': ['age_group2diff2age_group'],
                   'tissue': tissue,
                   'age': age,
                   'cell': '',
                   'efo': '',
                   'datatype': domain,
                   'drug': drug,
                   'dose': '',
                   'time': '',
                   'case': '',
                   'control': '',
                   'dataset_type': '',
                   'gender': gender,
                   'species': 'human',
                   'up': [],
                   'down': []
                   }
    request_config = {"inputs": config_data, "mode": "meta2diff", "parameters": {
        "temperature": 0.8,
        "top_p": 0.2,
        "top_k": 3550,
        "n_next_tokens": 50,
        "random_seed": 137
    }}

    response = requests.post(API_URL, headers=headers, json=request_config)
    return str(response.json())
