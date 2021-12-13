from sys import argv
from requests import get
from json import loads, dumps


def parse_changes(files: list, map: dict) -> bool:
    changelog = {"added": [], "renamed": [], "removed": [], "modified": []}
    nums = ()
    for file in files:

        status = file['status']
        filename = file['filename']

        nums += (map[status],) 

        if status == 'renamed':
            changelog['renamed'].append([file["previous_filename"], filename])
        else:
            changelog[status].append(filename)

    return changelog, min(nums)

def get_data(url: str, token: str) -> str:
    return get(url, headers={'Authorization': f'token {token}'}).json()

def add_to_tag(tag: list, index: int) -> list:
    while len(tag) < index: tag.append(0)
    tag[index-1] += 1
    return tag


if __name__ == '__main__':

    token, repo, change_map, separator, commits = argv[1:]

    commits = loads(commits.replace('\\n', '').replace("'", "\\'"))
    change_map = loads(change_map.replace('\\n', '').replace("'", "\\'"))

    files = []
    commit_messages = []
    for commit in commits:
        data = get_data(f'https://api.github.com/repos/{repo}/commits/{commit["id"]}', token)
        if 'files' in data:
            for file in data['files']:
                files.append(file)
        if 'commit' in data:
            commit_messages.append(data['commit']['message'])
    changelog, lowest = parse_changes(files, change_map)

    # check every commit name that starts with [+X]
    pot_lowest = [int(m.split('[+')[1].split(']')[0]) for m in commit_messages if m.startswith('[+')]
    if pot_lowest: lowest = min(pot_lowest)

    try:
        tag = get_data(f'https://api.github.com/repos/{repo}/tags', token)[0]['name']
    except IndexError:
        tag = '0.0.0'
    tag = [int(''.join(i for i in value if i.isdigit())) for value in tag.split(separator)]
    add_to_tag(tag, lowest)
    tag = separator.join([str(i) for i in tag])

    changelog_str = ''
    for change, values in changelog.items():
        if values:
            # %0A is just \n but for github action translation purposes
            if change == 'renamed':
                changes = ''.join([f'%0A• `{value[0]}` → `{value[1]}`' for value in values])+'%0A'
            else:
                changes = ''.join([f'%0A• `{value}`' for value in values])+'%0A'
            changelog_str += f'{change.title()}: {changes}'

    print('::set-output name=tag::'+tag)
    print('::set-output name=raw-changelog::'+dumps(changelog))
    print('::set-output name=changelog::'+changelog_str)