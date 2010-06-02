
import sys
import random

from guts.midichords import ChordSequencer
from guts.wiimote import Wiitar
from guts.guitar import Guitar, WiitarGuitarAdapter


def main():
    if len(sys.argv) < 2:
        print "Usage: python wiitar.py BDADDR"
        return
    
    wiitar = Wiitar(sys.argv[1])
    WiitarGuitarAdapter(Guitar(ChordSequencer()), wiitar)
    wiitar.start()

if __name__ == "__main__":
    main()
