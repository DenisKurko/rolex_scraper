import json
from typing import Any
import pandas
import requests
from requests.adapters import HTTPAdapter, Retry

# SET UP FUNCTIONS #
def get_model_spec(
    model: str, session: requests.Session
) -> dict[str, Any]:
    """ 
    Return given model specifications 
    """
    API_LINK = f'https://www.rolex.com/api/catalog/watches/{model}?language=en'
    model_spec_raw_json = session.get(API_LINK).text
    model_spec_json: dict = json.loads(model_spec_raw_json)
    
    # check if given model exist
    if 'error' in  model_spec_json and model_spec_json['error'] == 'no model found with these parameters':
        raise ValueError(f'Specified model ({model}) not found')
    
    # set dict for next import to Pandas DataFrame
    
    model_img_json = json.loads(model_spec_json['editorial_mapping']['cover']['lightbox_image_landscape_cl'])
    model_img = model_img_json[0]['src']
        
    model_spec_dict = {model:{
                            'Name': model_spec_json['name'],
                            'Img (URL)': f'https://media.rolex.com/image/upload/{model_img}',
                            'Model case': model_spec_json['case']['labels']['title'],
                            'Bezel': model_spec_json['case']['labels']['bezel'],
                            'Oyster architecture': model_spec_json['case']['labels']['oyster_architecture'],
                            'Diameter': model_spec_json['case']['labels']['diameter'],
                            'Material': model_spec_json['case']['labels']['material'],
                            'Winding crown': model_spec_json['case']['labels']['winding_crown'],
                            'Crystal': model_spec_json['case']['labels']['crystal'],
                            'Water resistance': model_spec_json['case']['labels']['water_resistance'],
                            
                            'Movement': model_spec_json['movement']['labels']['title'],
                            'Calibre': model_spec_json['movement']['labels']['calibre'],
                            'Precision': model_spec_json['movement']['labels']['precision_static'],
                            'Functions': model_spec_json['movement']['labels']['functions'],
                            'Oscillator': model_spec_json['movement']['labels']['oscillator'],
                            'Winding': model_spec_json['movement']['labels']['winding'],
                            'Power reserve': model_spec_json['movement']['labels']['tdr_movement_autonomy'],
                            
                            'Bracelet': model_spec_json['bracelet']['labels']['title'],
                            'Material': model_spec_json['bracelet']['labels']['material'],
                            'Clasp': model_spec_json['bracelet']['labels']['clasp_type'],

                            'Dial': model_spec_json['dial']['labels']['title'], 
                            'Details': model_spec_json['dial']['labels']['details'], 
                                
                            'Certification': model_spec_json['movement']['labels']['certification'],
                            'User guide': f'https://media.rolex.com/{model_spec_json['editorial_mapping']['userguide']['path_cl']}'
                            }
                       }
    
    return model_spec_dict

# SET UP REQUEST SESSION #
session = requests.Session()
retry_mod = Retry(total=20, backoff_max=0.1)
session.mount('https://', adapter=HTTPAdapter(max_retries=retry_mod))

# RECEIVE MODELS LIST #
MODELS_CATALOG_COUNT = 1500
MODELS_CATALOG_API_URL = f'https://www.rolex.com/api/catalog/watchgrid?language=en&numberOfResults={MODELS_CATALOG_COUNT}&grid=all'
models_catalog_raw_json = session.get(MODELS_CATALOG_API_URL).text
models_catalog_json: dict = json.loads(models_catalog_raw_json)

models_list: list[str] = [item['rmc'] for item in models_catalog_json['results']]

# SET MODELS INFO DICT #
models_spec_dict: dict[str, Any] = {}

model: str
for model in models_list:
    model_spec_dict = get_model_spec(model=model, session=session)
    models_spec_dict.update(model_spec_dict)
    
# SET PANDAS DATAFRAME #
models_dataFrame = pandas.DataFrame(models_spec_dict)
models_dataFrame = models_dataFrame.T

# SET EXCEL SHEET #
models_dataFrame.to_excel(excel_writer='Rolex_DataSheet.xlsx', sheet_name='MainPage')
