from DragonMaoMaoSpider.util.parser import YamlPareser
import urllib.parse
import redis
from rediscluster import StrictRedisCluster

class RedisDBClient(object):
    def __init__(self):
        self.ymlpaser = YamlPareser()
        self.redisdb = self.ymlpaser.get(key='Redis.conn')
        self.db = self.ymlpaser.get(self.redisdb, 'db') or 0
        self.pwd = self.ymlpaser.get(self.redisdb, 'pwd') or None
        self.client = self.create()

    def create(self):
        if self.ymlpaser.get(self.redisdb, 'nodes'):
            host_opt = []
            for r in self.redisdb['nodes']['members']:
                host_opt.append({"host":r['host'],"port":r['port']})
            return StrictRedisCluster(startup_nodes=host_opt, decode_responses=True)
        else:
            return redis.Redis(host=self.redisdb['host'], port=self.redisdb['port'], db=self.db, password=self.pwd)

    def close(self):
        pass

#singleton
redis_cli = RedisDBClient().client

if __name__ == '__main__':
    redis_cli.set('test','na')
    print(redis_cli.get('test'))
    redis_cli.delete('test')