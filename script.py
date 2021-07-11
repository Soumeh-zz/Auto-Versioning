from os import getenv
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from json import loads

token = getenv('TOKEN', '""')
payload = loads(getenv('PAYLOAD', '{"commits": []}'))
repo = loads(getenv('REPO', '{}'))

def get_commits(url: str, commits: list) -> list:
    try:
        before = commits[0]['timestamp']
        after = commits[-1]['timestamp']
    except IndexError:
        return []
    headers = {'Authorization': 'token '+token}
    rq = Request(url, headers=headers)
    try:
        json = urlopen(rq, data=bytes('{"accept": "application/vnd.github.v3+json", "since": "'+before+'", "until", "'+after+'"}', encoding='utf8')).read().decode('utf-8')
        return loads(json.json())
    except HTTPError:
        return []

def check_if_major(commits: list) -> bool:
    for commit in commits:
        if 'added' in commit or 'renamed' in commit:
            return True
    return False

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
    commits = get_commits(f'https://api.github.com/repos/{repo}/commits', payload['commits'])
    print(commits)
    if not commits:
        commits = payload['commits']
    major = check_if_major(commits)
    tag = get_latest_tag(f'https://api.github.com/repos/{repo}/tags')
    if not tag:
        tag = getenv('FALLBACK_TAG', '0.0')
    else:
        tag = gen_new_tag(major, tag)
    print('::set-output name=tag::'+tag)