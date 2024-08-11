import logging
import salt.config
import hvac  # 用于与HashiCorp Vault进行交互

log = logging.getLogger(__name__)

def get_vault_secret(client, key):
    """获取Vault中的密钥值"""
    try:
        secret = client.secrets.kv.v2.read_secret_version(path=key)
        return secret['data']['data']
    except Exception as e:
        log.error(f"Error retrieving secret {key}: {e}")
        return None

def targets(tgt, tgt_type="glob", **kwargs):
    __opts__ = salt.config.master_config('/etc/salt/master')

    # 从配置中获取 Vault 的相关信息
    vault_addr = __opts__.get('vault_addr', None)
    vault_token = __opts__.get('vault_token', None)
    vault_kv_path = __opts__.get('vault_kv_path', 'salt/roster')

    if not vault_addr or not vault_token:
        log.error("Vault address or token not found in the configuration.")
        return {}

    log.info(f"Connecting to Vault at {vault_addr}")

    # 创建 Vault 客户端
    client = hvac.Client(url=vault_addr, token=vault_token)
    
    # 如果 tgt_type 为多个对象，可以使用空格或者逗号进行分割，并移除两端的空格
    if tgt_type in ["list", "nodegroup"]:
        tgt_list = [t.strip() for t in tgt.split(",") if t.strip()]
    else:
        tgt_list = [tgt]

    host_configs = {}
    
    for host in tgt_list:
        secret = get_vault_secret(client, f"{vault_kv_path}/{host}")
        
        if secret:
            host_configs[host] = secret  # 直接使用从Vault KV中获取的数据

    log.info(f"Successfully retrieved {len(host_configs)} target hosts data.")
    return __utils__["roster_matcher.targets"](host_configs, tgt, tgt_type, "ipv4")