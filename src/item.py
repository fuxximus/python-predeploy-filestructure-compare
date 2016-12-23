from filecmp import dircmp
import os

class BlankItem:
    def __init__(self):
        self.path = ''

class Item(BlankItem):
    def __init__(self, path, name):
        self.path = path
        self.name = name

        self.displayName = (name[:48] + '..') if len(name) > 50 else name
        self.isDifferent = False
        self.isDirectory = False
        self.isLatest = False
        self.isIgnored = False
        self.differenceType = 'base'
        self.parent = BlankItem()

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()

    def getColor(self):
        return {
            'added': '#0a0',
            'removed': '#ffafaf',
            'edited': '#b57536',
            'base': '#000',
            'not_present': '#aaa'
        }[self.differenceType]

    def setDifferenceType(self,value):
        self.differenceType = value
        if value != 'base':
            self.isDifferent = True


class Directory(Item):
    def __init__(self, path, name):
        Item.__init__(self, path, name)
        self.displayName = ((name[:48] + '..') if len(name) > 50 else name)+'/'
        self.isDirectory = True
        self.items = []

    def __str__(self):
        return self.name+self.items.__repr__()

    def __repr__(self):
        return self.__str__()

    def indexOf(self, item):
        for i in range(len(self.items)):
            if self.items[i].name == item.name and self.items[i].isDirectory == item.isDirectory:
                return i
        return -1

    def append(self, item):
        i = self.indexOf(item)
        item.parent = self
        if i < 0:
            self.items.append(item)
        else:
            self.items[i] = item


class Version:
    def __init__(self, path, isBase = False):
        self.path = path
        self.isBase = isBase
        self.root = Directory('', '')
        self.root.parent = Item('','')

class Comparison:
    def __init__(self, left, right, name):
        self.left = left
        self.right = right
        self.name = name
        self.combined = Directory('','')

    def compare(self, git_ignore = [], ignore_svn = True):
        ignores = []
        ignores.extend(git_ignore)

        if(ignore_svn):
            ignores.append('.svn')

        dcmp = dircmp(self.left.path, self.right.path, ignores)
        different = self.doComparison(dcmp,self.left.root,self.right.root, self.combined, 0, git_ignore)
        self.left.root.isDifferent = different

    def doComparison(self, dcmp, lft_directory, rgt_directory, combined, depth = 0, git_ignore = []):
        _all = []
        _all.extend(dcmp.common_files)
        _all.extend(dcmp.left_only)
        _all.extend(dcmp.right_only)
        _all = sorted(_all, key=str.lower)

        isDifferent = False
        keys = sorted(dcmp.subdirs.keys(), key=str.lower)
        for key in keys:
            self_path = lft_directory.path+'/'+key
            self_path_wild_flag = lft_directory.path+'/*'

            lft_new_directory = Directory(self_path, key)
            rgt_new_directory = Directory(self_path, key)
            new_directory = Directory(self_path, key)
            new_directory.setDifferenceType('not_present')
            lft_directory.append(lft_new_directory)
            rgt_directory.append(rgt_new_directory)
            combined.append(new_directory)
            # print('path:',self_path.strip('/\\\n')+'</br>')
            # print('path (wild card):',self_path_wild_flag.strip('/\\\n')+'</br>')
            if self_path.strip('/\\\n') not in git_ignore and self_path_wild_flag.strip('/\\\n') not in git_ignore:
                # if key in dcmp.right_only:
                #     new_directory = Directory(self_path, key)
                #     new_directory.setDifferenceType('removed')
                #     new_directory.isActual = False
                #     isDifferent = True
                #     rgt_directory.append(new_directory)
                # elif key in dcmp.left_only:
                #     new_directory = Directory(self_path, key)
                #     new_directory.setDifferenceType('added')
                #     isDifferent = True
                #     lft_directory.append(new_directory)
                # else:
                tmp = self.doComparison(dcmp.subdirs[key], lft_new_directory, rgt_new_directory, new_directory, depth + 1, git_ignore)
                lft_new_directory.isDifferent = tmp
                rgt_new_directory.isDifferent = tmp

                if tmp:
                    isDifferent = tmp
                    lft_new_directory.setDifferenceType('edited')
                    if not self.right.isBase:
                        rgt_new_directory.setDifferenceType('edited')
            else:
                new_directory.isIgnored = True
                lft_new_directory.isIgnored = True
                rgt_new_directory.isIgnored = True

        for item in _all:
            self_path = combined.path+'/'+item
            self_path_wild_flag = combined.path+'/*'

            combined_item = Item(self_path, item)
            new_item = Item(self_path, item)
            isIgnored = False

            if self_path.strip('/\\\n') in git_ignore or self_path_wild_flag.strip('/\\\n') in git_ignore:
                isIgnored = True

            new_item.isIgnored = isIgnored
            combined_item.isIgnored = isIgnored

            if item in dcmp.diff_files:
                isDifferent = True
                rgt_item = Item(self_path, item)
                new_item.setDifferenceType('edited')
                if not self.right.isBase:
                    rgt_item.setDifferenceType('edited')
                rgt_directory.append(rgt_item)
                lft_directory.append(new_item)
            elif item in dcmp.right_only:
                rgt_item = Item(self_path, item)
                if os.path.isdir(self.right.path+self_path):
                    new_item = Directory(self_path, item)
                    rgt_item = Directory(self_path, item)
                    combined_item = Directory(self_path, item)
                    combined_item.isIgnored = isIgnored
                    self.readNewFolder(rgt_item, combined_item, self.right.path+self_path)

                new_item.isIgnored = isIgnored
                rgt_item.isIgnored = isIgnored
                if self.right.isBase:
                    new_item.setDifferenceType('removed')
                    lft_directory.append(new_item)
                    rgt_directory.append(rgt_item)
                isDifferent = True
            elif item in dcmp.left_only:
                if os.path.isdir(self.left.path+self_path):
                    new_item = Directory(self_path, item)
                    combined_item = Directory(self_path, item)
                    self.readNewFolder(new_item, combined_item, self.left.path+self_path)
                new_item.setDifferenceType('added')
                lft_directory.append(new_item)
                isDifferent = True
            else:
                rgt_item = Item(self_path, item)
                rgt_item.isIgnored = isIgnored
                rgt_directory.append(rgt_item)
                lft_directory.append(new_item)


            combined_item.setDifferenceType('not_present')
            combined.append(combined_item)
        return isDifferent

    def readNewFolder(self, directory, combined, absolute_path):
        items = os.listdir(absolute_path)
        for item in items:
            self_path = directory.path+'/'+item
            if os.path.isdir(absolute_path+'/'+item):
                new_item = Directory(self_path, item)
                combined_item = Directory(self_path, item)
                self.readNewFolder(new_item, combined_item, absolute_path+'/'+item)
            else:
                new_item = Item(self_path, item)
                combined_item = Item(self_path, item)

            new_item.setDifferenceType('added')

            directory.append(new_item)
            combined_item.setDifferenceType('not_present')
            combined.append(combined_item)
