import os
import requests
import json
import patoolib
from bs4 import BeautifulSoup
import pandas as pd
from itertools import accumulate
import tsm
import random
from base64 import b64decode, b64encode

#file name for steam cdn servers list storage
servers_list_filename = "list_of_steam_cdn_servers.json"


#builds the html file path
def get_html_file_path(depotid, manifestid):
    
    #Takes: the depotid (char)
    #Returns: the depot file path (char)
    
    return depotid + "_" + manifestid + ".html"

#builds the url to the steamdb depot
def get_steamdb_depot_url(depotid):
    
    #Takes: the depotid (char)
    #Returns: the depot steamdb url (char)
    
    return "https://steamdb.info/depot/"+ depotid

#downloads (scrapes) depot html page from steamdb
def get_html(depotid, manifestid):

    #Takes: The depotid (char)
    #Returns: Nothing
    
    #The html file path to write to (char)
    
    html_file_path = get_html_file_path(depotid, manifestid)
    
    #Checks if the file exists
    
    if not os.path.isfile(html_file_path):
    
    #If not, then:
    
    #The html page steamdb url (char)
    
     html_page_url = get_steamdb_depot_url(depotid)
    
    #Executes the curl command as a subcommand on the steamdb url of the given depotid
    
     os.system("curl "+ html_page_url + " -o " + html_file_path)
    
def get_list_of_servers_url():
    
    #Takes: Nothing
    #Returns: the url to grab the json file which contains the servers list
    
    return "https://api.steampowered.com/IContentServerDirectoryService/GetServersForSteamPipe/v1/?"
        
    
def get_list_of_servers():
    
    #Takes: Nothing
    #Returns: Nothing
        
    #The url of servers list
    
    servers_list_url = get_list_of_servers_url()
    
    #Grab the servers list from the url in form of json 
    
    servers_list_data = requests.get(servers_list_url, stream=True).content
    
    #Store it in the json file
    
    with open(servers_list_filename, "wb") as servers_list_file:
     servers_list_file.write(servers_list_data)

#lists steam cdn servers from json file
def list_servers():
    
    #Takes: Nothing
    #Returns: the list of servers

    #Opens the json file that constains servers list 
    if not os.path.isfile(servers_list_filename):
     get_list_of_servers()
    
    file_servers_download = open(
        servers_list_filename, mode='rb')
    
    #Declares servers list
    
    servers = []
    
    #Parses the json file
    
    response = json.load(file_servers_download)
    
    #Extracts each server's protocol and host
    
    for entry in response['response']['servers']:
     server = '%s://%s' % (
         'https' if entry['https_support'] == 'mandatory' else 'http',
         entry['host']
     )
     
    #Adds each server to the list
    
     servers.append(server)
     
    return servers


#picks up a random server each time (to avoid saturation)
def random_server():

    #Takes: Nothing 
    #Returns: A random server from the servers list
    
    #The list of servers (protocol://host/)
    
    list_of_servers = list_servers()
    
    return random.choice(list_of_servers)


#downloads the manifest from cdn or cache server
def download_manifest(depotid, manifestid):
    
    #Takes: Two arguments:
     #1)The depotid of the manifest
     #2)The manifestid of the manifest
    #Returns: The raw data contained in the manifest
    
    #Checks if the manifests directory exists
    
    if not os.path.isdir('manifests_'+manifestid):
    
    #If not, creates it
    
     os.mkdir('manifests_'+manifestid)
     
    #Declares the path of the manifest
     
    manifest_path = 'manifests_'+manifestid+'/z'
    
    #Checks if the manifest exists
    
    if not os.path.isfile(manifest_path):
    
    #Declares the zip archive file path
    
     archive_zip_path = 'manifest_'+manifestid+'.zip'  
     
    #Checks if it exists
    
     if not os.path.isfile(archive_zip_path):
     
    #If not, declares the random server url to download the manifest from
    
      server_url = str(random_server())
    
    #And downloads it
    
      manifest_download = requests.get(
         server_url+'/depot/'+depotid+'/manifest/'+manifestid+'/5', stream=True).content
         
    #And writes its content to a zip archive
    
      with open(archive_zip_path, 'wb') as manifest:
       manifest.write(manifest_download)
      
    #Extracts the manifest from the archive and writes it to the manifests folder
    
     patoolib.extract_archive(
         archive_zip_path, outdir='manifests_'+manifestid)
         
    #Removes the archive
    
     os.remove('manifest_'+manifestid+'.zip')
    
    return open(manifest_path, 'rb').read()


#analyzes the html page to extract data 
def scrape_database(depotid, manifestid):
    
    #Takes: the depotid of the depot to get data from
    #Returns: Nothing
    
    #Declares the data of the depot scraped from steamdb and written to the html file
    
    if not os.path.isfile(get_html_file_path(depotid, manifestid)):
     get_html(depotid, manifestid)

    raw_html_data = open(get_html_file_path(depotid, manifestid), 'rb')
    
    #Parses the raw html data with BeautifulSoup
    
    soup = BeautifulSoup(raw_html_data, features="html.parser")
    
    #Find proper sizes html tag, which is td
    
    sizes_tags = soup.findAll('td')
    
    #Find proper sizes strings, which are attributes of sizes_tags
    
    proper_db_sizes = [size.attrs['data-sort']
                          for size in sizes_tags if 'data-sort' in size.attrs]
                          
    #Find all textual html strings, which contains all other data than proper sizes (plain filenames, filetypes, file sizes with suffixes)
                          
    text = soup.find_all(text=True)
    
    #Declares a texts list which excludes "\n" terminators
    
    non_n = [t for t in text if not t == '\n']
    
    #Keeps the part which contains data mentionned above only (otherwise they become undeterminable from blobs): 
    
     #Declares the index of the beginning for parsing the html file
    
    index_of_beginning = non_n.index('Initializing table…')
    
     #Declares the index of the finishing for parsing the html file
    
    index_of_finishing = non_n.index('File types')
    
     #Deletes the part before the index of the beginning
    
    del non_n[int(index_of_finishing):len(non_n)]
    
     #Deletes the part after the index of the finishing
    
    del non_n[0:int(index_of_beginning)+1]
    
    #Find indices of folders (files that have type "Folder")
    
    folders = [i for i, x in enumerate(non_n) if x == "Folder"]
    
    #Find indices of files without extension
    
    files_without_extension = [n for n in non_n if not n.split(
        '/')[0] == n and n.split('.')[0] == n and non_n[non_n.index(n)+1].endswith('B')]
    
    #Declares a list that includes both
    
    indices_to_append_none = [n for n in range(0, len(non_n)-1) if non_n[n] in files_without_extension or n in folders]
    
    #Adds "None" element after each one (Adds null filesize to folders, and none extension to files without)
    
    for n in indices_to_append_none:
    
      non_n.insert(n+1+indices_to_append_none.index(n), 'None')
      
    #Checks if an installscript is in the main list 
    
    if 'InstallScript' in non_n:
    
    #If so, determines its index
    
     installscript_index = non_n.index('InstallScript')
     
    #And deletes it from the main list
    
     del non_n[installscript_index]
     
    #Lists indexes of useless zeros of proper sizes list (they index is pair)
    
    useless_zeros = [n for n in range(
        0, len(proper_db_sizes)-1) if (n % 2) == 0]
        
    #Deletes them
    
    for useless_zero in useless_zeros:
    
     del proper_db_sizes[useless_zero-useless_zeros.index(useless_zero)]
     
    #Replaces null proper sizes (which are presented as being equal -1 ) by zeros (0)
    
    proper_db_sizes[:] = ['0' if x
                             == '-1' else x for x in proper_db_sizes]                            
    
    #Computes the lenght of the list of triples from the main list 
    
    triples_list_length  = len(non_n)//3
    
    #Declares a list of the same lenght which describes a tuple with 3 as its elements lenght
    
    description_list = []
    
    #Adds the number of elements to the list (3 subelements by element)
    
    for n in range(triples_list_length):
    
     description_list.append(3)
     
    #Regroup files data by triples, each triple containing its name, type and size
    
    triples_list = [non_n[x - y: x] for x, y in zip(accumulate(description_list), description_list)]
    
    #Creates the lists from the triples list (filenames, filestypes, filesizes with suffixes)
    
    file_names = [triple[0] for triple in triples_list]
    
    file_types = [triple[1] for triple in triples_list]
    
    file_sizes_with_suffixes = [triple[2] for triple in triples_list]
    
    
    #Deletes text numbers which are not proper db sizes (Beginning from the number of filenames)
    
    del proper_db_sizes[len(file_names):len(proper_db_sizes)]
    
    print(len(proper_db_sizes))
    print(proper_db_sizes)
    
    
    #Saves data to their respective txt files:
    
     #Verifies if the plain names file exists
    
    if not os.path.isfile(depotid+'_plain_names.txt'):
    
     #If not, writes plain names to it    
     
     with open(depotid+'plain_names.txt', 'w') as f:
     
      f.write(json.dumps(file_names))
     
     #Verifies if the plain sizes file exists
     
    if not os.path.isfile(depotid+'_plain_sizes.txt'):
     
     #If not, writes plain sizes to it
     
     with open(depotid+'_plain_sizes.txt', 'w') as f:
     
      f.write(json.dumps(proper_db_sizes))

#deserializes the manifest with the ValvePython API
def deserialize_manifest(depotid, manifestid):

    #Takes: Two Arguments:
    #1)The depotid of the manifest
    #2)The manifestid of the manifest
    #Returns: A dictionnary containing encrypted names, manifest sizes, and hashs

    #Gets data from the manifest
    
    data = download_manifest(depotid=depotid, manifestid=manifestid)
    
    #Gets manifest file sizes
    
    manifest_file_sizes = tsm.encrypted_file_sizes(
            data=data)
    
    #Gets manifest file hashs
    
    hashs = tsm.hashs(data=data)
    
    #Gets base64 serialized manifest file names
    
    encrypted_file_names = tsm.encrypted_files_base64(data=data)
    
    #Creates a dictionnary of files data (file names, file sizes, hashs)
    
    manifest_files = {
            "encrypted_names": encrypted_file_names,
            "manifest_sizes": manifest_file_sizes,
            "hashs": hashs
        }
    df = pd.DataFrame(manifest_files)
    return df.set_index("encrypted_names")
  


#filters and orders plain data and cipher data
def prepararing_cryptanalysis(depotid, manifestid):

    #Takes: Two Arguments:
     #1) the depotid
     #2) the manifestid
    #Returns: Nothing
    
    #Checks if the plain names and plain sizes lists files exists 
    
    if not os.path.isfile(depotid+'_plain_names.txt') or not os.path.isfile(depotid+'_plain_sizes.txt'):
    
     #If not, then create them through scraping the database
     
     scrape_database(depotid=depotid, manifestid=manifestid)

    #Parses the json plain names list file 
    
    plain_db_names = json.loads(open(depotid+'_plain_names.txt', 'rb').read())
    
    #Parses the json plain sizes list file 
    
    sizes_db = json.loads(open(depotid+'_plain_sizes.txt', 'rb').read())

    #Creates the list of manifest sizes
    
    sizes_manifest = [str(t) for t in deserialize_manifest(
        depotid=depotid, manifestid=manifestid).__getitem__("manifest_sizes")]
      
    #Creates the list of manifest encrypted names
    
    encrypted_manifest_names = deserialize_manifest(
        depotid=depotid, manifestid=manifestid).__getitem__("encrypted_names")
        
    #Deletes folders (their names and sizes), their sizes being 0, so highly indistiguishable between plain and manifest files
    
    #Lists the indexes of the manifest file sizes of folders (0)
    
    encrypted_indexes = [index for index, value in enumerate(
        sizes_manifest) if value == '0']
        
    if not len(encrypted_indexes) == 0:
     
     for n in encrypted_indexes:
     
      #Deletes the folders encrypted file names
      
      encrypted_manifest_names.remove(
          encrypted_manifest_names[n-encrypted_indexes.index(n)])
    
      #Deletes the folders manifest file sizes
    
      sizes_manifest.remove(sizes_manifest[n-encrypted_indexes.index(n)])

    #Lists the indexs of the plain file sizes of folders(0)

    plain_indexs = [index for index,
                     value in enumerate(sizes_db) if value == '0']
    if not len(plain_indexs) == 0:
     for n in plain_indexs:
     
       #Deletes the folders plain file names
       
       plain_db_names.remove(noms_clairs_db[n-plain_indexs.index(n)])
       
       #Deletes the folders plain file sizes
       
       sizes_db.remove(sizes_db[n-plain_indexs.index(n)])

    #Deletes repeated sizes files (names and sizes), so highly indistinguishable between plain and manifest files
    
    #Lists the index of the plain files of repeated sizes
    
    indexs = [[sizes_db.index(c) for c in sizes_db if c == k]
              for k in set(sizes_db)]
    
    
    repeated_files_indexs = [n for n in indexs if len(n) > 1]
    if not len(repeated_files_indexs) == 0:
     b = [k[1] for k in repeated_files_indexs]
     f = [sizes_db[n] for n in b]
     plain_index = [index for index,
                     value in enumerate(sizes_db) if value in f]
     encrypted_index = [index for index, value in enumerate(
         sizes_manifest) if value in f]
     for n in plain_index:
        plain_db_names.remove(plain_db_names[n-plain_index.index(n)])
        sizes_db.remove(sizes_db[n-plain_index.index(n)])
     for n in encrypted_index:
        encrypted_manifest_names.remove(
            encrypted_manifest_names[n-encrypted_index.index(n)])
        sizes_manifest.remove(sizes_manifest[n-encrypted_index.index(n)])
    #Remettre les noms cryptés en ordre
    ordered_indexs = [sizes_manifest.index(n) for n in sizes_db]
    encrypted_names = []
    for n in range(0, len(encrypted_manifest_names)):
     encrypted_names.append(encrypted_manifest_names[ordered_indexs[n]])
    sizes_c = []
    for n in range(0, len(sizes_manifest)):
     sizes_c.append(sizes_manifest[ordered_indexs[n]])
    encrypted_and_plain_index = {
        "noms_clairs": plain_db_names,
        "tailles": sizes_db,
        "noms_chiffrés": encrypted_names
    }
    df = pd.DataFrame(encrypted_and_plain_index)
    df.set_index("noms_clairs")
    print(df)


if __name__ == '__main__':
    #Checks the file doesn't already exist
     
    print(deserialize_manifest("731", "2364687932903859561"))
