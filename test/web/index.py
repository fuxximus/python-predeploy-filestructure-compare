#!D:/programs/python3/python.exe
import cgi
import cgitb
import sys
sys.path.insert(0,"../../src")
from item import Item, Directory
from filecmp import dircmp

cgitb.enable()



folder2 = '../data/deployed.prod'
folder1 = '../data/current.prod'
folder3 = '../data/rc'
use_gitignore =  True
ignore_svn = True

form = cgi.FieldStorage()
form_posted = False
if 'submit' in form:
    form_posted = True
    folder1 = form['folder1'].value if 'folder1' in form else 'D:\projects\loan.mobile.resources\lab'
    folder2 = form['folder2'].value if 'folder2' in form else 'D:\projects\loan.mobile.resources\lab'
    folder3 = form['folder3'].value if 'folder3' in form else 'D:\projects\loan'
    use_gitignore = False if 'use_gitignore' not in form or form['use_gitignore'].value == 'off' else True
    ignore_svn = False if 'ignore_svn' not in form or form['ignore_svn'].value == 'off' else True

def printRow(item, lft_color, rgt_color, indent):
    print(('<tr>'+
    '<td style="padding-left:{padding}px">'+
    ('<span style="color: {lft_color}">'+item+'</span>')+
    '</td><td style="padding-left:{padding}px">'+
    ('<span style="color: {rgt_color}">'+item+'</span>')+
    '</td></tr>').format(padding = indent*10, lft_color = lft_color, rgt_color = rgt_color))

def doComparison(dcmp, path, indent = 0, git_ignore = []):
    _all = []
    _all.extend(dcmp.common_files)
    _all.extend(dcmp.left_only)
    _all.extend(dcmp.right_only)
    _all = sorted(_all, key=str.lower)


    keys = sorted(dcmp.subdirs.keys(), key=str.lower)
    for key in keys:
        self_path = path+'/'+key
        self_path_wild_flag = path+'/*'
        # print('path:',self_path.strip('/\\\n')+'</br>')
        # print('path (wild card):',self_path_wild_flag.strip('/\\\n')+'</br>')
        if self_path.strip('/\\\n') not in git_ignore and self_path_wild_flag.strip('/\\\n') not in git_ignore:
            printRow(key,'#000','#000', indent)
            doComparison(dcmp.subdirs[key],self_path, indent + 1, git_ignore)

    for item in _all:
        lft_color = '#000'
        rgt_color = '#000'
        skip = False
        self_path = path+'/'+item
        self_path_wild_flag = path+'/*'


        if self_path.strip('/\\\n') not in git_ignore and self_path_wild_flag.strip('/\\\n') not in git_ignore:
            if item in dcmp.diff_files:
                lft_color = '#b25f00'
                rgt_color = '#b25f00'
            elif item in dcmp.right_only:
                lft_color = '#aaa'
            elif item in dcmp.left_only:
                rgt_color = '#aaa'
            else:
                skip = True
        else:
            skip = True

        truncated = (item[:48] + '..') if len(item) > 50 else item

        if not skip:
            printRow(truncated, lft_color, rgt_color, indent)


def compareFolders(left, right, git_ignore = [], ignore_svn = True):
    ignores = []
    ignores.extend(git_ignore)

    if(ignore_svn):
        ignores.append('.svn')

    dcmp = dircmp(left, right,ignores)
    print('<table style="width:100%;" class=\'data\' ><tbody>')
    doComparison(dcmp,'', 0,git_ignore)
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


print("Content-type: text/html")
print()
print("<html>")
print("<head>")
print("<link href=\"/css/main.css\" rel=\"stylesheet\" />")
print("<title>Predeploy Compare</title>")
print("</head>")
print("<body>")
print("<h1>Compare</h1>")
print("""<div><form method='post'>
    <label for='folder1'>Current PROD: </label><input type='text' id='folder1' value="{folder1_value}" name='folder1'/>
    <label for='folder2'>Last Deploy PROD: </label><input type='text' id='folder2' value="{folder2_value}" name='folder2'/>
    <label for='folder2'>RC: </label><input type='text' id='folder2' name='folder3' value="{folder3_value}"/>
    <label for='use_gitignore'>.gitignore: </label><input type='checkbox' id='use_gitignore' name='use_gitignore' {use_gitignore}/>
    <label for='ignore_svn'>ignore .svn: </label><input type='checkbox' id='ignore_svn' name='ignore_svn' {ignore_svn}/>
    <input type='submit' value='go' name='submit'/>
</form></div>""".format(folder1_value=folder1, folder2_value = folder2, folder3_value = folder3, use_gitignore=('checked=\"checked\"' if use_gitignore else ''), ignore_svn=('checked=\"checked\"' if ignore_svn else '')))
print("<div>")
print("""<div style="width:50%;padding:10px;float:left;">
        <h4>RC <-> Previous Deployment</h4>""")
compareFolders(folder3, folder2, git_ignores, ignore_svn)
print("""</div>
    <div style="width:50%;padding:10px;float:left;">
        <h4>Current Prod <-> Previous Deployment</h4>""")
compareFolders(folder1, folder2, git_ignores, ignore_svn)
print("""</div>
    <div class='clear'/>
</div>
<div style="width:40%;margin-left: auto; margin-right:auto;">
    <h4>RC <-> Current Prod</h4>""")
compareFolders(folder3, folder1, git_ignores, ignore_svn)
print("""</div>
""")
print("</body>")
print("</html>")
