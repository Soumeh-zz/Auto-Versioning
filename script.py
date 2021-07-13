from os import getenv
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from json import loads

token = getenv('TOKEN', '""')
payload = loads(getenv('PAYLOAD', '{"before": "", "after": ""}'))
repo = loads(getenv('REPO', '{}'))

def get_files(url: str) -> list:
    headers = {'Authorization': 'token '+token}
    print(url)
    rq = Request(url, headers=headers)
    try:
        json = urlopen(rq, data=bytes('{"accept": "application/vnd.github.v3+json"}', encoding='utf8')).read().decode('utf-8')
        print(loads(json.json()))
        return loads(json.json())['files']
    except HTTPError:
        return []

def parse_changes(files: list) -> bool:
    changelog = {"added": [], "renamed": [], "deleted": [], "changed": []}
    major = False
    for file in files:
        status = file['status']
        filename = file['filename']
        if status == 'renamed':
            if not major:
                major = True
            changelog['renamed'].append('`'+file['old_name']+'` → `'+file['new_name']+'`')
        if status == 'added':
            if not major:
                major = True
            changelog['added'].append('`'+filename+'`')
        if status == 'removed':
            changelog['deleted'].append('`'+filename+'`')
        if status == 'changed':
            changelog['deleted'].append('`'+filename+'`')
    return changelog, major

def get_latest_tag(url: str) -> str:
    headers = {'Authorization': 'token '+token}
    rq = Request(url, headers=headers)
    try:
        json = urlopen(rq, data=bytes('{"accept": "application/vnd.github.v3+json"}', encoding='utf8')).read().decode('utf-8')
        return loads(json.json())[0]['name']
    except HTTPError:
        return None

def gen_new_tag(major: bool, tag: str) -> str:
    tag = ''.join([i for i in tag if i.isnumeric() or i == '.']).split('.')
    tag = [int(i) for i in tag]
    if major:
        try:
            tag[1] += 1
        except IndexError:
            tag.append(0)
    else:
        try:
            tag[2] += 1
        except IndexError:
            tag.append(0)
            if len(tag) < 2:
                tag.append(0)
    return '.'.join(tag)

if __name__ == '__main__':
    files = get_files(f'https://api.github.com/repos/{repo}/compare/{payload["before"]}...{payload["after"]}')
    print(files)
    changelog, major = parse_changes(files)
    tag = get_latest_tag(f'https://api.github.com/repos/{repo}/tags')
    if not tag:
        tag = getenv('FALLBACK_TAG', '0.0')
    else:
        tag = gen_new_tag(major, tag)
    changelog_str = ''
    for change, values in changelog.items():
        if values:
            changelog_str += change.title()+': '+'\n- '.join(values)+'\n'
    print('::set-output name=tag::'+tag)
    print('::set-output name=changelog::'+changelog_str)