import yaml
import configparser
import os
from approot import get_root

class YamlPareser(object):
    def __init__(self,filename = os.path.join(get_root(),'config.yml')):
        self.configs = yaml.load(open(filename,'r'))

    def get(self, configs=None, key=None):
        if not configs:
            configs = self.configs
        try:
            value = configs.get(key)
            return value
        except Exception:
            return None

class IniConfPareser(object):
    def __init__(self,filname):
        self.config = configparser.ConfigParser()
        self.config.read(filname)

    def get(self, section=None, key=None):
        try:
            return self.config.get(section,key)
        except Exception:
            return None

if __name__ == '__main__':
    #configs = ConfigParser()
    #mysql_conn = configs.get(server='',key='conn')
    #print(mysql_conn)
    yml = get_root()  + '\\config.yml'
    ymlpaser = YamlPareser(yml)
    conn = ymlpaser.get(key = 'MongoDB.conn')
    print(conn)
    host = ymlpaser.get(conn, 'host')
    print(host)
    db = ymlpaser.get('db')
    print(db)