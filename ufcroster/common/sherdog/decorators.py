from functools import wraps


def disallow_none_return(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if result is None:
            raise ValueError(f'None returned by {func.__name__}')
        return result
    return wrapper


def ignore_attr_err(fn=None, default=None):
    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except AttributeError:
                return default
        return wrapper

    if fn:
        return decorate(fn)
    return decorate
