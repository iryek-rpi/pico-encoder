CH_TCP = 1      # channel to host
CH_SERIAL = 0

TEXT_PORT = 2004
CRYPTO_PORT = 8502

PARITY_NONE = 'N'
PARITY_EVEN = 0
PARITY_ODD = 1

CHANNEL_OPTIONS = (0, ['TCP', '시리얼'])
PARITY_OPTIONS = (0, [PARITY_NONE, PARITY_EVEN, PARITY_ODD])
DATA_OPTIONS = (1, [7, 8])
STOP_OPTIONS = (0, [1, 2])
SPEED_OPTIONS = (0, [9600, 19200, 38400])

MY_IP = 'ip'
CONFIG = 'config'
GATEWAY = 'gateway'
SUBNET = 'subnet'
PEER_IP = 'peer_ip'
HOST_IP = 'host_ip'
HOST_PORT = 'host_port'
SPEED = 'speed'
PARITY = 'parity'
DATA = 'data'
STOP = 'stop'
CHANNEL = 'channel'
KEY = 'key'
