# Maybe Monad

def __concatMap__(f, m):
    return None if m is None else f(m)

def __singleton__(x):
    return x

def __fail__():
    return None

def ret(x):
    return __singleton__(x)

print [
    x
    for x in 242
    for y in x + 30
    for z in y + 40
    for q in None]

