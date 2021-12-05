def weight(weight):
    """ Make able to put weight in classes or functions by decorator @weight"""
    def decorator(func):
        func.weight = weight
        return func

    return decorator
