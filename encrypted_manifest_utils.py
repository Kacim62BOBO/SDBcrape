from steam.core.manifest import DepotManifest
from base64 import b64decode

def get_encrypted_files_sizes(data):
    c = DepotManifest(data)
    return [c.DepotFileClass(c, mapping).file_mapping.size for mapping in c.payload.mappings]

def get_encrypted_filenames_base64(data):
    c = DepotManifest(data)
    return [b64decode(c.DepotFileClass(c, mapping).file_mapping.filename) for mapping in c.payload.mappings]

def get_chunks_hashs(data):
    c = DepotManifest(data)
    return [c.DepotFileClass(c, c.payload.mappings[0]).file_mapping.chunks]

def get_files_count(data):
    c = DepotManifest(data)
    return len(c.payload.mappings)
