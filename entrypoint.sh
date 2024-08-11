#!/bin/bash
# Set default password if SALTAPI_PASSWORD not provided

sed -i "s|VAULT_ADDR_PLACEHOLDER|${VAULT_ADDR}|g" /etc/salt/master
sed -i "s|VAULT_KV_PATH_PLACEHOLDER|${VAULT_KV_PATH}|g" /etc/salt/master
sed -i "s|VAULT_TOKEN_PLACEHOLDER|${VAULT_TOKEN}|g" /etc/salt/master

DEFAULT_SALTAPI_PASSWORD="saltapi"
SALTAPI_PASSWORD=${SALTAPI_PASSWORD:-$DEFAULT_SALTAPI_PASSWORD}

# Change password for saltapi user
echo "saltapi:$SALTAPI_PASSWORD" | chpasswd
# Run command passed into docker run
exec "$@"