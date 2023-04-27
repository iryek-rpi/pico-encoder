import json

config = {'key1': 'value1', 'key2': 'value2'}

f = open('config.json', 'w')
f.write(ujson.dumps(config))
f.close()

import json

f = open('config.json', 'r')
c = ujson.loads(f.readall())

#edit the data
config['key3'] = 'value3'

#write it back to the file
f = open('config.json', 'w')
f.write(ujson.dumps(config))
f.close()
 

 >>> d = {}
>>> d['dict1']['innerkey1'] = 'value1'
>>> d['dict2']['innerkey2'] = 'value2'
{'dict1': {'innerkey1': 'value1'},'dict2': {'innerkey2': 'value2'}}
