import json
from ..core.config import settings

BASE_URL = settings.BASE_URL


def get_code_samples(route, method):
    nl = "\n"  # new line character to use in f-strings.
    header = {}
    cookies = {}
    if method in ["POST", "PUT", "DELETE", "GET"]:
        try:
            example_schema = route.body_field.type_.Config.schema_extra.get("example")
            payload = f"json.dumps({example_schema})"
            data_raw = (
                f"\\{nl} --data-raw " + "'" + f"{json.dumps(example_schema)} " + "'"
            )
        except Exception as e:
            print(f"Path:{route.path} Error:{e}")
            payload = "{}"
            data_raw = ""

    else:
        payload = "{}"
        data_raw = ""

    return [
        {
            "lang": "Shell",
            "source": f"curl --location\\{nl} "
            f"--request {method} '{BASE_URL}{route.path}'\\{nl} "
            f"--header {header}"
            f"--cookie {cookies}{nl}"
            f"{data_raw}",
            "label": "Curl",
        },
        {
            "lang": "Python",
            "source": f"import requests{nl}"
            f"{'import json' + nl if method.lower() == 'post' else ''}{nl}"
            f'url = "{BASE_URL}{route.path}"{nl}'
            f"payload = {payload}{nl}"
            f"headers = {header}{nl}"
            f"cookies = {cookies}{nl}"
            f'response = requests.request("{method}", url, headers=headers, data=payload){nl}'
            f"print(response.text)",
            "label": "Python3",
        },
    ]
