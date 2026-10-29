"""Prepare an optional, verified portable Blender for Scholar asset authoring.

Does not install system-wide, change PATH, or affect game runtime requirements.
"""
from pathlib import Path
import argparse
import hashlib
import urllib.request
import zipfile

ROOT=Path(__file__).resolve().parents[1]
VERSION='4.5.15'
FOLDER=f'blender-{VERSION}-windows-x64'
ARCHIVE=FOLDER+'.zip'
URL='https://download.blender.org/release/Blender4.5/'+ARCHIVE
SHA256='52dd02fd74877fa08e74b67d7854cf32468a232c02aaa19b6844c91285574f8d'
SIZE=398649826

def digest(path):
    value=hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda:source.read(1024*1024),b''):value.update(block)
    return value.hexdigest()

def prepare(download=False):
    base=(ROOT/'data'/'character-tools').resolve();base.mkdir(parents=True,exist_ok=True)
    archive=base/ARCHIVE
    if not archive.is_file() or archive.stat().st_size!=SIZE or digest(archive)!=SHA256:
        if not download:raise RuntimeError('Verified portable Blender is missing. Use --download for the pinned official archive.')
        partial=base/(ARCHIVE+'.partial');count=0;progress=0
        with urllib.request.urlopen(URL,timeout=60) as source,partial.open('wb') as output:
            while block:=source.read(1024*1024):
                count+=len(block)
                if count>SIZE:raise RuntimeError('Archive exceeds pinned size.')
                output.write(block)
                if count-progress>=50*1024*1024:progress=count;print('Downloaded',count//(1024*1024),'MiB',flush=True)
        if partial.stat().st_size!=SIZE or digest(partial)!=SHA256:raise RuntimeError('Archive verification failed; nothing was installed.')
        partial.replace(archive)
    executable=base/FOLDER/'blender.exe'
    if not executable.is_file():
        print('Extracting verified portable Blender...',flush=True)
        with zipfile.ZipFile(archive) as bundle:
            for item in bundle.infolist():
                target=(base/item.filename).resolve()
                if not target.is_relative_to(base/FOLDER):raise RuntimeError('Unexpected archive path.')
            bundle.extractall(base)
    if not executable.is_file():raise RuntimeError('Verified archive did not provide expected Blender binary.')
    print(str(executable),flush=True)
    return executable

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--download',action='store_true');prepare(parser.parse_args().download)
