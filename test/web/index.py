#!D:/programs/python3/python.exe
import cgi
import cgitb
from filecmp import dircmp

cgitb.enable()



folder1 = 'D:\projects\loan.mobile.resources\lab'
folder2 = 'D:\projects\loan.mobile.resources\lab'
folder3 = 'D:\projects\loan'
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
    '</td></tr>').format(padding = indent*5, lft_color = lft_color, rgt_color = rgt_color))

def doComparison(dcmp, path, indent = 0):
    _all = []
    _all.extend(dcmp.common_files)
    _all.extend(dcmp.left_only)
    _all.extend(dcmp.right_only)
    _all = sorted(_all, key=str.lower)



    for key in dcmp.subdirs.keys():
        self_path = path+'/'+key
        printRow(key,'#000','#000', indent)
        doComparison(dcmp.subdirs[key],self_path, indent + 1)

    for item in _all:
        lft_color = '#000'
        rgt_color = '#000'

        if item in dcmp.diff_files:
            lft_color = '#b25f00'
            rgt_color = '#b25f00'
        elif item in dcmp.right_only:
            lft_color = '#ccc'
        elif item in dcmp.left_only:
            rgt_color = '#ccc'

        printRow(item, lft_color, rgt_color, indent)


def compareFolders(left, right, git_ignore = [], ignore_svn = True):
    ignores = []
    ignores.extend(git_ignore)

    if(ignore_svn):
        ignores.append('.svn')

    #print(ignores)
    dcmp = dircmp(left, right,ignores)
    print('<table style="width:100%"><tbody>')
    doComparison(dcmp,'', 0)
    print('</tbody></table>')

def readGitIgnoresToList(_dir):
    retarr = []
    with open(_dir+'/.gitignore') as fin:
        for line in fin:
            retarr.append(line.strip('/\\\n'))

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
print(git_ignores)
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
