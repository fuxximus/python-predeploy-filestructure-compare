#!D:/programs/python3/python.exe
import cgi
import cgitb
import sys
sys.path.insert(0,"../../src")
from item import Item, Directory, Version, Comparison
from filecmp import dircmp

cgitb.enable()

folder1 = '../data/current.prod'
folder2 = '../data/deployed.prod'
folder3 = '../data/rc'
use_gitignore =  True
ignore_svn = True
identical = True

form = cgi.FieldStorage()
form_posted = False
if 'submit' in form:
    form_posted = True
    folder1 = form['folder1'].value if 'folder1' in form else folder1
    folder2 = form['folder2'].value if 'folder2' in form else folder2
    folder3 = form['folder3'].value if 'folder3' in form else folder3
    use_gitignore = False if 'use_gitignore' not in form or form['use_gitignore'].value == 'off' else True
    ignore_svn = False if 'ignore_svn' not in form or form['ignore_svn'].value == 'off' else True
    identical = False if 'identical' not in form or form['identical'].value == 'off' else True

def printRow(item, lft_color, rgt_color, _class, onClick, indent):
    print(('<tr class="'+_class+(' item' if indent > 1 else '')+'" onclick="'+onClick+'">'+
    '<td style="padding-left:{padding}px">'+
    '<span style="color: {lft_color}">'+item+'</span>'+
    '</td><td style="padding-left:{padding}px">'+
    '<span style="color: {rgt_color}">'+item+'</span>'+
    '</td></tr>').format(padding = indent*10, lft_color = lft_color, rgt_color = rgt_color))



def printItem(left_item, right_item, combined, prefix, depth):
    if not left_item.isIgnored and (left_item.isDifferent or not identical):
        if left_item.isDirectory:
            path =  prefix + combined.parent.path.replace('/','_').replace('\\','_')
            self_path = prefix + combined.path.replace('/','_').replace('\\','_')

            printRow(combined.displayName, left_item.getColor(), right_item.getColor(),path, 'toggleFolder(\''+self_path+'\')' if path!=self_path else '', depth)
            #print((' '*depth)+left_item.name,'item count:',len(left_item.items))
            for i in range(len(combined.items)):
                left_index = left_item.indexOf(combined.items[i])
                right_index = right_item.indexOf(combined.items[i])
                if left_index >-1 and right_index > -1:
                    printItem(left_item.items[left_index], right_item.items[right_index], combined.items[i], prefix, depth+1)
                elif left_index < 0 and right_index > -1:
                    printItem(combined.items[i], right_item.items[right_index], combined.items[i], prefix, depth+1)
                elif right_index < 0 and left_index > -1:
                    printItem(left_item.items[left_index], combined.items[i], combined.items[i], prefix, depth+1)
        else:
            printRow(combined.displayName, left_item.getColor(), right_item.getColor(), prefix + combined.parent.path.replace('/','_').replace('\\','_'), '',depth)


def compareFolders(left, right, name, git_ignore = [], ignore_svn = True):
    comparison = Comparison(left, right, name)
    comparison.compare(git_ignore, ignore_svn)
    print('<table style="width:100%;" class=\'data\' ><tbody>')
    #print(left.root)
    printItem(left.root, right.root, comparison.combined, comparison.name, 0)
    print('</tbody></table>')

def readGitIgnoresToList(_dir):
    retarr = []
    try:
        with open(_dir+'/.gitignore') as fin:
            for line in fin:
                retarr.append(line.strip('/\\\n'))
    except OSError as e:
        retarr = []

    return retarr


git_ignores = readGitIgnoresToList(folder3)

rc = Version(folder3)
base = Version(folder2, True)
prod = Version(folder1)

print("Content-type: text/html")
print()
print("""<html>
  <head>
    <script src="/js/main.js"></script>
    <script src="/js/jquery-3.1.1.min.js"></script>
    <link href=\"/css/main.css\" rel=\"stylesheet\" />
    <title>Predeploy Compare</title>
  </head>
    <body>
        <h1>Compare</h1>""")
print("""<div><form method='post'>
    <label for='folder1'>Current PROD: </label><input type='text' id='folder1' value="{folder1_value}" name='folder1'/>
    <label for='folder2'>Last Deploy PROD: </label><input type='text' id='folder2' value="{folder2_value}" name='folder2'/>
    <label for='folder2'>RC: </label><input type='text' id='folder2' name='folder3' value="{folder3_value}"/>
    <label for='use_gitignore'>.gitignore: </label><input type='checkbox' id='use_gitignore' name='use_gitignore' {use_gitignore}/>
    <label for='ignore_svn'>ignore .svn: </label><input type='checkbox' id='ignore_svn' name='ignore_svn' {ignore_svn}/>
    <label for='ignore_svn'>hide identical: </label><input type='checkbox' id='identical' name='identical' {identical}/>
    <input type='submit' value='go' name='submit'/>
</form></div>""".format(folder1_value=folder1, folder2_value = folder2, folder3_value = folder3, use_gitignore=('checked=\"checked\"' if use_gitignore else ''), ignore_svn=('checked=\"checked\"' if ignore_svn else ''), identical=('checked=\"checked\"' if identical else '')))
print("<div>")
print("""<div style="width:50%;padding:10px;float:left;">
        <h4>RC <-> Previous Deployment</h4>""")

compareFolders(rc, base, 'rc_base', git_ignores, ignore_svn)
print("""</div>
    <div style="width:50%;padding:10px;float:left;">
        <h4>Current Prod <-> Previous Deployment</h4>""")
compareFolders(prod, base, 'curr_base', git_ignores, ignore_svn)
print("""</div>
    <div class='clear'/>
</div>
<div style="width:40%;margin-left: auto; margin-right:auto;">
    <h4>RC <-> Current Prod</h4>""")
compareFolders(rc, prod, 'rc_curr', git_ignores, ignore_svn)
print("""</div>
""")
print("</body>")
print("</html>")
