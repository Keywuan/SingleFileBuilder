#   IMPORTS
import win32api
from win32api import mouse_event,keybd_event
from time import sleep
import time
import os

#   DEPENDENCY 'derek.py'
class derek(object):
    
    
    i = 32
    def test_test():
        print(derek.i)
    
    def ha_ha():
        print(derek.test_test())


#    FIXED FROM IMPORTS
test_test = derek.test_test

#   MAIN FILE 'main.py'
print("Hello World!")
x = 99
test_test()
