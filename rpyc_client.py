import rpyc

s = rpyc.connect('localhost', 18861)
c = s.root

print c.pow(2,3)  # Returns 2**3 = 8
print c.add(2,3)  # Returns 5
print c.div(5,2)  # Returns 5//2 = 2

while True:
    c.slowprint('This is a test string')
