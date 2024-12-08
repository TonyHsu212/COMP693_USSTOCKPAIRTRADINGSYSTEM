from flask_hashing import Hashing


def _init():
    global _global_dict
    _global_dict = {}


def set_value(key, value):
    #'define function to set global value'
    _global_dict[key] = value


def get_value(key, defValue=None):
    #define function to get global value
    try:
        return _global_dict[key]
    except KeyError:
        return 'there is no defult value'


