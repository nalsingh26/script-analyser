from bs4 import BeautifulSoup as bs44
from bs4 import BeautifulSoup as bs
import urllib3
import os
import random
import sys

DESC_TAG = 'DESCRIPTION'

#Method to download all scripts from all genres hosted at www.imsdb.com
#This is quite crude and specific to parsing the imsdb format
def get_scripts():
    save_to = 'C:\\Users\\nalin\\OneDrive\\Documents\\Python Scripts\\Script-Analyzer-master\\scripts_clean\\'
    http = urllib3.PoolManager()
    url = 'http://www.imsdb.com/all%20scripts/'
    response = http.request('GET', url)
    soup = bs(response.data, features="lxml")
    count = 0
    lost = []
    for link in soup.findAll('a'):
        url = link.get('href')
        if url.startswith('/Movie Scripts/'):
            name = (url.split('/')[2])[:-11].strip()
            name = name.replace(':','')
            name = name.replace('?','')
            file_name = name
            name = '-'.join([n.strip() for n in name.split(' ')])
            print('--',(name))
            try:
                html = http.request('GET','http://www.imsdb.com/scripts/'+name+'.html')
                sp = bs44(html.data,"html.parser")
                
                text = sp.get_text()
                lines = [''.join([i if ord(i)<128 else ' ' for i in line]) for line in text.splitlines()]
                filtered = []
                started = False
                for line in lines:
                    if line.upper().strip() == 'ALL SCRIPTS':
                        started = True
                    elif line.startswith('Writers : '):
                        started = False
                    if started == True:
                        filtered.append(line)

                script = '\n'.join(filtered)
                print(file_name)
                with open(save_to+file_name+'.txt','a') as sc_file:
                    sc_file.write(script)
            except Exception as e:
                print(e)
                count = count+1
                lost.append(file_name)
    print(lost)

#Method to load script(s). Returns a list of tuples: (movie name,lines of script)
#Setting count = N will return N random scripts
#Specifiying a name will load only that script
def load_scripts(path,count=None,name=None):
    scripts = []
    if not name is None:
        return [(name,open(path+name).readlines())]
    files = os.listdir(path)
    if count is None:
        count = len(files)
    else:
        random.shuffle(files)
    for sc_file in files[:count]:
        scripts.append((sc_file,open(path+sc_file).readlines()))
    return scripts

#Auxiliary method to remove all non-ASCII characters in text - cleans unknown characters
def clean(text):
    return ''.join([c if ord(c)<128 else '' for c in text])
