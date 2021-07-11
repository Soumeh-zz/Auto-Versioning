from os import getenv
from urllib.request import Request, urlopen
from json import loads

token = getenv('TOKEN', '""')
commits = loads(getenv('COMMITS', '[]'))
repo = loads(getenv('REPO', '{}'))

def check_if_major(commits: list) -> bool:
    for commit in commits:
        if 'added' in commit or 'renamed' in commit:
            return True
    return False

def get_latest_tag(url: str) -> str:
    headers = {'Authorization': 'token '+token}
    rq = Request(url, headers=headers)
    print(rq)
    json = urlopen(rq, data=bytes('{"accept": "application/vnd.github.v3+json"}', encoding='utf8')).read().decode('utf-8')
    print(json)
    return loads(json.json())[0]

def gen_new_tag(tag: str) -> str:
    major = check_if_major(commits)
    tag = get_latest_tag(f'https://api.github.com/repos/{repo}/tags')
    tag = ''.join([i for i in tag if i.isnumeric() or i == '.'].split('.'))
    tag = [int(i) for i in tag]
    if major:
        tag[1] += 1
    else:
        tag[2] += 1
    return '.'.join(tag)

if __name__ == '__main__':
    print(token)
    print(commits)
    print(repo)
    major = check_if_major(commits)
    tag = get_latest_tag(f'https://api.github.com/repos/{repo}/tags')
    tag = gen_new_tag(tag)
    print('::set-output name=tag::'+tag)