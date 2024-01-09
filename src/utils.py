def to_iterable(obj: object) -> list | set:
    return obj if isinstance(obj, (list, set)) else [obj]