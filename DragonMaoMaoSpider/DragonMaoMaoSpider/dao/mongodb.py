from DragonMaoMaoSpider.util.parser import YamlPareser
import pymongo
import urllib.parse

class MongoDBClient(object):
    def __init__(self):
        self.ymlpaser = YamlPareser()
        self.mongodb = self.ymlpaser.get(key='MongoDB.conn')
        self.db = self.ymlpaser.get(self.mongodb,'db') or 'test'
        self.client = self.create()

    def create(self):
        if self.ymlpaser.get(self.mongodb, 'nodes'):
            host_opt = []
            for m in self.mongodb['nodes']['members']:
                host_opt.append('%s:%s' % (m['host'], m['port']))
            replicaSet = self.mongodb['replicaSet']['name']
        else:
            host_opt = '%s:%s' % (self.mongodb['host'], self.mongodb['port'])
            replicaSet = None

        option = {
            'host': host_opt,
            'authSource': self.db,
            'replicaSet': replicaSet,
        }
        if self.ymlpaser.get(self.mongodb,'user') and self.ymlpaser.get(self.mongodb,'pwd'):
            # py2中为urllib.quote_plus
            option['username'] = urllib.parse.quote_plus(self.mongodb['user'])
            option['password'] = urllib.parse.quote_plus(self.mongodb['pwd'])
            option['authMechanism'] = 'SCRAM-SHA-1'
        #print(option)
        return pymongo.MongoClient(**option)

    def insert(self, collect, dic):
        self.client[self.db][collect].insert(dic)

    def find(self, collect, dic):
        pass

    def remove(self, collect, dic):
        pass

    def close(self):
        if self.client:
            self.client.close()

#singleton
mongodb_cli = MongoDBClient()

if __name__ == '__main__':
    #configs = ConfigParser()
    #mysql_conn = configs.get(server='',key='conn')
    #print(mysql_conn)
    client = MongoDBClient()
    client.insert('phq', {'name': 'phq','age': 26})
    client.remove('phq',{'name':'phq'})
    client.close()


