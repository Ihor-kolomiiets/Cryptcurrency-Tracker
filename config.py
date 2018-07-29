from enum import Enum

token = ''  # bot token
database = ''  # database name


#  States class
class States(Enum):
    S_CLEAR_STATE = '0'
    S_ADD_CRYPTO = '1'
    S_DELETE_CRYPTO = '2'
