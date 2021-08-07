import pprint

LOGGER = False


def logger(func):
    global LOGGER
    if LOGGER:
        def wrapper(*args, **kwargs):
            print('args'.center(40, '_'))
            for num, value in enumerate(args, 1):
                print(f'arg{num} -> {value}')
            print('kwargs'.center(40, '_'))
            for arg, value in kwargs.items():
                print(f'{arg} -> {value}')
            res = func(*args, **kwargs)
            try:
                print(f"""Request""".center(40, '_'))
                print(f"""url: {res.request.url}\nbody: {res.request.body}""")
                print("Response".center(40, '_'))
                print(f"""status_code: {res.status_code}\njson: {pprint.pformat(res.json(), indent=2)}""")
            except KeyError:
                ...
            return res

        return wrapper
    else:
        return func
