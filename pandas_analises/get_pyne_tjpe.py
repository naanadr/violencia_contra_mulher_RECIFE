import json

import pymongo


COLLECTION_NAME = 'pyne_tjpe_ouvidoria'
CONNECTION = ('mongodb://intelivix:cBcUWHAwYqZ6TYPoM6ekPPoW@mongodb.primary.intelivix.com:3000')

client = pymongo.MongoClient(CONNECTION)

distintos = set()
# for numero in client.tribunais[COLLECTION_NAME].aggregate([{'$group': {'_id': '$numero'}}]):
#     distintos.add(numero['_id'])
with open('not_added.txt') as f:
    for line in f.readlines():
        distintos.add(line[:-1])

try:
    distintos_ = distintos.copy()
    for numero in distintos_:
        results = client.tribunais[COLLECTION_NAME].find({'numero': numero})
        for result in results:
            del result['_id']
            with open('pyne_tjpe_ouvidoria.jsonl', 'a') as f:
                f.write('{}\n'.format(json.dumps(result)))
        distintos.remove(numero)
except Exception as e:
    print(e)
    with open('not_added.txt', 'w') as f:
        for numero in distintos:
            f.write('{}\n'.format(numero))
