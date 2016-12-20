class item:
    isDifferent = False
    isDirectory = False
    differenceType = 'base'


class Directory(Item):
    isDirectory = True
    items = []
