class Item:
    isDifferent = False
    isDirectory = False
    isLatest = False
    differenceType = 'base'
    path = ''
    def getColor():
        return {
            'added': '#0a0',
            'removed': '#0061ff',
            'edited': '#a50',
            'base': '#000',
            'conflict': '#a00',
            'not_present': '#aaa'
        }[self.differenceType]


class Directory(Item):
    isDirectory = True
    items = []

class Version:
    root = Directory()
