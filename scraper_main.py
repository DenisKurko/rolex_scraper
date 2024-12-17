import json
from typing import Any
import pandas
import requests
from scraper_funcs import get_model_spec
from requests.adapters import HTTPAdapter, Retry

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
