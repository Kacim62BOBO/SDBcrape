import os
import sys

#Gets the manifest changes file name
def Get_manifest_history_filename(depotid, manifestid):
    return depotid+"_"+manifestid+"_manifest_changes.html"

#Gets the url of all manifests change history
def Get_url_of_manifests_history(depotid):
    return "https://steamdb.info/depot/"+depotid+"/history/"

#Gets the manifests history list
def Get_manifests_history(depotid):

#Gets url of the specified manifest change history
def Get_url_of_manifest_history(depotid, manifestid):
    return "https://steamdb.info/depot/"+depotid+"/history/?changeid=M:"+manifestid

#Downloads the manifest history to the file
def Get_page_of_manifest_history_data(depotid, manifestid):

    print("Downloading changes list for manifestid "+manifestid)
    fname = Get_manifest_history_filename(depotid, manifestid)
    url = Get_page_of_manifest_history_data(depotid, manifestid)
    cmd = "fetcher --target='InnerText' --url="+url+" --output='"+fname+"'"
    os.system(cmd)

#Gets the manifest creation date
def Get_manifest_date(depotid, manifestid):

#Parses the manifest chages file
def Parse_manifest_history:
    fname = Get_manifest_history_filename(depotid, manifestid)
    file = open(fname, "r")

#Get steamdb manifest
def 


