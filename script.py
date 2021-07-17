from os import getenv
from requests import get
from json import loads

token = getenv('TOKEN', '')
commits = loads(getenv('COMMITS', '[]'))
repo = getenv('REPO', '')

def parse_changes(files: list) -> bool:
    changelog = {"added": [], "renamed": [], "deleted": [], "changed": []}
    major = False
    for file in files:
        status = file['status']
        if not major:
            if status == 'renamed' or status == 'added':
                major = True
        filename = file['filename']
        if filename in changelog['deleted']:
            continue
        if status == 'renamed':
            changelog['renamed'].append('`'+file['previous_filename']+'` → `'+filename+'`')
        if status == 'added':
            changelog['added'].append('`'+filename+'`')
        if status == 'removed':
            changelog['deleted'].append('`'+filename+'`')
        if status == 'modified':
            changelog['changed'].append('`'+filename+'`')
    return changelog, major

def get_data(url: str) -> str:
    return get(url, headers={'Authorization': 'token '+token}).json()

def gen_new_tag(major: bool, tag: str) -> str:
    tag = ''.join([i for i in tag if i.isnumeric() or i == '.']).split('.')
    try:
        tag = [int(i) for i in tag]
    except ValueError:
        return getenv('FALLBACK_TAG', '0.0')
    if major:
        try:
            tag[1] += 1
        except IndexError:
            tag.append(0)
        tag[2] = 0
    else:
        try:
            tag[2] += 1
        except IndexError:
            tag.append(0)
            if len(tag) < 2:
                tag.append(0)
    return '.'.join([str(i) for i in tag])

if __name__ == '__main__':
    commit_ids = [commit['id'] for commit in commits]
    files = []
    for commit_id in commit_ids:
        files += get_data(f'https://api.github.com/repos/{repo}/commits/{commit_id}')['files']
    changelog, major = parse_changes(files)
    try:
        tag = get_data(f'https://api.github.com/repos/{repo}/tags')[0]['name']
    except IndexError:
        tag = getenv('FALLBACK_TAG', '0.0')
    else:
        tag = gen_new_tag(major, tag)
    changelog_str = ''
    for change, values in changelog.items():
        if values:
            changelog_str += f'{change.title()}: '+''.join(['%0A• '+value for value in values])+'%0A'
    print('::set-output name=tag::'+tag)
    print('::set-output name=changelog::'+changelog_str)