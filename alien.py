from datetime import datetime, timezone, timedelta
import time
from logger import log, _log
import logging
import requests
import functools
from eosapi import NodeException, TransactionException, EosApiException, Transaction
from nonce import Nonce, generate_nonce
from eosapi import EosApi
from typing import List, Dict, Union, Tuple
import random
from settings import user_param, interval
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.ssl_ import create_urllib3_context
import tenacity
from tenacity import wait_fixed, RetryCallState, retry_if_not_exception_type
from requests import RequestException
from dataclasses import dataclass


class CipherAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        context = create_urllib3_context(ciphers='DEFAULT:@SECLEVEL=2')
        kwargs['ssl_context'] = context
        return super(CipherAdapter, self).init_poolmanager(*args, **kwargs)

    def proxy_manager_for(self, *args, **kwargs):
        context = create_urllib3_context(ciphers='DEFAULT:@SECLEVEL=2')
        kwargs['ssl_context'] = context
        return super(CipherAdapter, self).proxy_manager_for(*args, **kwargs)


class StopException(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)



@dataclass
class HttpProxy:
    proxy: str
    user_name: str = None
    password: str = None

    def to_proxies(self) -> Dict:
        if self.user_name and self.password:
            proxies = {
                "http": "http://{0}:{1}@{2}".format(self.user_name, self.password, self.proxy),
                "https": "http://{0}:{1}@{2}".format(self.user_name, self.password, self.proxy),
            }
        else:
            proxies = {
                "http": "http://{0}".format(self.proxy),
                "https": "http://{0}".format(self.proxy),
            }
        return proxies



class Alien:
    # alien_host = "https://aw-guard.yeomen.ai"

    def __init__(self, wax_account: str, token: str, charge_time: int, proxy: HttpProxy = None):
        self.wax_account: str = wax_account
        self.token: str = token
        self.log: logging.LoggerAdapter = logging.LoggerAdapter(_log, {"tag": self.wax_account})
        self.http = requests.Session()
        self.http.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, " \
                                          "like Gecko) Chrome/101.0.4951.54 Safari/537.36 "
        self.http.trust_env = False
        self.http.request = functools.partial(self.http.request, timeout=60)
        self.http.mount('https://public-wax-on.wax.io', CipherAdapter())
        self.rpc_host = user_param.rpc_domain
        self.eosapi = EosApi(self.rpc_host, timeout=60)
        if user_param.cpu_account and user_param.cpu_key:
            self.eosapi.set_cpu_payer(user_param.cpu_account, user_param.cpu_key)

        if proxy:
            proxies = proxy.to_proxies()
            self.http.proxies = proxies
            self.eosapi.session.proxies = proxies

        retry = tenacity.retry(retry = retry_if_not_exception_type(StopException), wait=self.wait_retry, reraise=False)
        self.mine = retry(self.mine)
        self.query_last_mine = retry(self.query_last_mine)

        self.charge_time: int = charge_time
        self.next_mine_time: datetime = None

        self.trx_error_count = 0

    def wait_retry(self, retry_state: RetryCallState) -> float:
        exp = retry_state.outcome.exception()
        wait_seconds = interval.transact
        if isinstance(exp, RequestException):
            self.log.info("网络错误: {0}".format(exp))
            wait_seconds = interval.net_error
        elif isinstance(exp, NodeException):
            self.log.info((str(exp)))
            self.log.info("节点错误,状态码【{0}】".format(exp.resp.status_code))
            wait_seconds = interval.transact
        elif isinstance(exp, TransactionException):
            self.trx_error_count += 1
            self.log.info("交易失败： {0}".format(exp.resp.text))
            if "is greater than the maximum billable" in exp.resp.text:
                self.log.error("CPU资源不足，可能需要质押更多WAX，稍后重试 [{0}]".format(self.trx_error_count))
                wait_seconds = interval.cpu_insufficient
            elif "is not less than the maximum billable CPU time" in exp.resp.text:
                self.log.error("交易被限制,可能被该节点拉黑 [{0}]".format(self.trx_error_count))
                wait_seconds = interval.transact
            elif "NOTHING_TO_MINE" in exp.resp.text:
                self.log.error("账号可能被封，请手动检查 ERR::NOTHING_TO_MINE")
                raise StopException("账号可能被封")
        else:
            if exp:
                self.log.info("常规错误: {0}".format(exp), exc_info=exp)
            else:
                self.log.info("常规错误")
        if self.trx_error_count >= interval.max_trx_error:
            self.log.info("交易连续出错[{0}]次，为避免被节点拉黑，脚本停止，请手动检查问题或更换节点".format(self.trx_error_count))
            raise StopException("交易连续出错")
        self.log.info("{0}秒后重试: [{1}]".format(wait_seconds, retry_state.attempt_number))
        return float(wait_seconds)


    def get_table_rows(self, table: str):
        post_data = {
            "json": True,
            "code": "m.federation",
            "scope": "m.federation",
            "table": table,
            "lower_bound": self.wax_account,
            "upper_bound": self.wax_account,
            "index_position": 1,
            "key_type": "",
            "limit": 10,
            "reverse": False,
            "show_payer": False
        }
        return self.eosapi.get_table_rows(post_data)

    # 采矿
    def mine(self) -> bool:
        # 查询上次采矿的信息
        last_mine_time, last_mine_tx = self.query_last_mine()

        ready_mine_time = last_mine_time + timedelta(seconds=self.charge_time)
        if datetime.now() < ready_mine_time:
            interval_seconds = self.charge_time + random.randint(user_param.delay1, user_param.delay2)
            self.next_mine_time = last_mine_time + timedelta(seconds=interval_seconds)
            self.log.info("时间不到,下次采矿时间: {0}".format(self.next_mine_time))
            return False

        time.sleep(interval.req)
        self.log.info("开始采矿")
        # 生成nonce
        nonce = generate_nonce(self.wax_account, last_mine_tx)
        nonce = nonce.random_string

        self.log.info("生成 nonce: {0}".format(nonce))

        # 调用合约，序列化交易
        trx = {
            "actions": [{
                "account": "m.federation",
                "name": "mine",
                "authorization": [{
                    "actor": self.wax_account,
                    "permission": "active",
                }],
                "data": {
                    "miner": self.wax_account,
                    "nonce": nonce,
                },
            }]
        }
        trx = self.eosapi.make_transaction(trx)
        serialized_trx = list(trx.pack())

        # wax云钱包签名
        signatures = self.wax_sign(serialized_trx)
        time.sleep(interval.req)
        trx.signatures.extend(signatures)
        self.push_transaction(trx)

        interval_seconds = self.charge_time + random.randint(user_param.delay1, user_param.delay2)
        self.next_mine_time = datetime.now() + timedelta(seconds=interval_seconds)
        self.log.info("下次采矿时间: {0}".format(self.next_mine_time))

        return True


    def push_transaction(self, trx: Union[Dict, Transaction]):
        self.log.info("开始交易: {0}".format(trx))
        resp = self.eosapi.push_transaction(trx)
        self.log.info("交易成功, transaction_id: [{0}]".format(resp["transaction_id"]))
        self.trx_error_count = 0


    def wax_sign(self, serialized_trx: str) -> List[str]:
        self.log.info("正在通过云钱包签名")
        url = "https://public-wax-on.wax.io/wam/sign"
        post_data = {
            "serializedTransaction": serialized_trx,
            "description": "jwt is insecure",
            "freeBandwidth": False,
            "website": "play.alienworlds.io",
        }
        headers = {"x-access-token": self.token}
        resp = self.http.post(url, json=post_data, headers=headers)
        if resp.status_code != 200:
            self.log.info("签名失败: {0}".format(resp.text))
            if "Session Token is invalid" in resp.text:
                self.log.info("token失效，请重新获取")
                raise StopException("token失效")
            else:
                raise NodeException("wax server error: {0}".format
                                    (resp.text), resp)

        resp = resp.json()
        self.log.info("签名成功: {0}".format(resp["signatures"]))
        return resp["signatures"]


    def query_last_mine(self) -> Tuple[datetime, str]:
        self.log.info("正在查询上次采矿信息")
        resp = self.get_table_rows("miners")
        resp = resp["rows"][0]
        self.log.info("上次采矿信息: {0}".format(resp))
        last_mine_time = datetime.fromisoformat(resp["last_mine"])
        last_mine_time = last_mine_time.replace(tzinfo=timezone.utc)
        last_mine_time = last_mine_time.astimezone()
        last_mine_time = last_mine_time.replace(tzinfo=None)
        self.log.info("上次采矿时间: {0}".format(last_mine_time))
        return last_mine_time, resp["last_mine_tx"]


    def run(self):
        try:
            self.mine()
            while True:
                if datetime.now() > self.next_mine_time:
                    self.mine()
                time.sleep(1)
        except StopException as e:
            self.log.info("采矿停止")
        except Exception as e:
            self.log.exception("采矿异常: {0}".format(str(e)))
