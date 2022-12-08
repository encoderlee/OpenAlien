from typing import List, Dict, Optional
from dataclasses import dataclass
from dacite import from_dict, Config


class interval:
    req: int = 2
    net_error: int = 5
    transact: int = 20
    cpu_insufficient: int = 60
    max_trx_error: int = 10

@dataclass
class UserParam:
    rpc_domain: str = "https://wax.pink.gg"
    cpu_account: Optional[str] = None
    cpu_key: Optional[str] = None
    delay1: int = 30
    delay2: int = 90
    claimmines: int = 10

    proxy: Optional[str] = None
    proxy_username: Optional[str] = None
    proxy_password: Optional[str] = None

    account: str = None
    token: str = None
    charge_time: int = None


user_param: UserParam = UserParam()


def load_param(data: Dict) -> UserParam:
    user = from_dict(UserParam, data, config = Config(type_hooks={str: str}))
    user_param.__dict__ = user.__dict__
