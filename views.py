import json
from typing import Tuple

from src.client import Request


def ping(request: Request) -> Tuple[int, str]:
    respnose_data = {
        'status': 'success',
        'data': 'pong'
    }
    return 200, json.dumps(respnose_data)


# @server.post('/convert')
# def convert(request: Request) -> Tuple[int, str]:
#     try:
#         data = json.loads(request.data)
#     # TODO im not sure that this is correct exception
#     except json.decoder.JSONDecodeError:
#         return 415, json.dumps({'error': 'Unsupported Media Type'})
#
#     # validate data
#     if not isinstance(data, dict) or 'amount' not in data or \
#             not (
#                     isinstance(data['amount'], int) or
#                     isinstance(data['amount'], float)
#             ) or data['amount'] < 0:
#         return 400, json.dumps({'error': 'Wrong params'})
#
#     # not best decision to make request every time, because data updated hourly
#     # for example, we can store this data on server side and update them also hourly
#     rub_rate, state_at = get_rate()
#
#     respnose_data = {
#         'result': round(data['amount'] * rub_rate, 2),
#         'from': 'USD',
#         'to': 'RUB',
#         'state_at': state_at
#     }
#     return 200, json.dumps(respnose_data)
#
#
# @server.status_404()
# def not_found(request: Request) -> Tuple[int, str]:
#     return 404, '''
#         <html>
#             <head>
#                 <title>page not found</title>
#             </head>
#             <body>
#                 <h1>404 not found</h1>
#             </body>
#         </html>'''
#
