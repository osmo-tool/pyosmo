def weight(value):
    """ Make able to put weight in classes or functions by decorator @weight"""

    def decorator(func):
        func.weight = value
        return func

    return decorator
