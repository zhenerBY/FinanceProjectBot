import requests


def api_request(method=None,
                url=None,
                headers=None,
                files=None,
                data=None,
                params=None,
                auth=None,
                cookies=None,
                hooks=None,
                json=None,
                **kwargs, ):
    headers = {} if headers is None else headers
    headers.update(
        {
            'Authorization': 'Api-Key ' + APIKEY,
        }
    )
    req = requests.Request(
        method=method,
        url=url,
        headers=headers,
        files=files,
        data=data,
        params=params,
        auth=auth,
        cookies=cookies,
        hooks=hooks,
        json=json,
    )
    r = req.prepare()
    s = requests.Session()
    return s.send(r)


def get_api_users_list(chat_id: int = None) -> list:
    if chat_id is not None:
        data = {
            'chat_id': chat_id,
        }
    else:
        data = {}
    url = HOST_API + 'apiusers/'
    users_data = api_request(method='GET', json=data, url=url)
    json_users_data = users_data.json()
    return json_users_data