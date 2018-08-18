import os
import platform

def get_root():
    return os.path.dirname( os.path.abspath( __file__ ) )

if __name__ == '__main__':
    print(os.path.join(get_root(),'aa.png'))