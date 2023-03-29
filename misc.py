from random import choice, randint

def namesystem_random():
    
    naming = [
        ["praha", "brno", "zbiroh", "kozojedy", "jicin", "stropkov", "liberec", "olomouc", "zdelov", "modrany", "zbraslav"],
        ["sever", "jih", "vychod", "zapad"]
    ]

    return "-".join((choice(naming[0]), choice(naming[1]), str(randint(0,99))))