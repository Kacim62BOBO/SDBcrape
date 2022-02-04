from steam.core.manifest import DepotManifest
from base64 import b64decode

def encrypted_file_sizes(data):
    c = DepotManifest(data)
    return [c.DepotFileClass(c, mapping).file_mapping.size for mapping in c.payload.mappings]

def encrypted_files_base64(data):
    c = DepotManifest(data)
    return [b64decode(c.DepotFileClass(c, mapping).file_mapping.filename) for mapping in c.payload.mappings]

def hashs(data):
    c = DepotManifest(data)
    return [c.DepotFileClass(c, mapping).file_mapping.chunks for mapping in c.payload.mappings]

