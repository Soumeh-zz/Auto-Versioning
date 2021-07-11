from os import getenv
from requests import get
from json import load

token = getenv('TOKEN')
commits = load(getenv('COMMITS', []))
repo = load(getenv('REPO'))

def check_if_major(commits: list) -> bool:
    for commit in commits:
        if 'added' in commit or 'renamed' in commit:
            return True
    return False

def get_latest_tag(url: str) -> str:
    headers = {'Authorization': 'token '+token}
    json = get(url, headers=headers, params={'accept': 'application/vnd.github.v3+json'})
    return load(json.json())[0]

def gen_new_tag(tag: str) -> str:
    major = check_if_major(commits)
    tag = get_latest_tag(f'https://api.github.com/repos/{repo}/tags')
    tag = ''.join([i for i if i.isnumeric() or i == '.']).split('.')
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