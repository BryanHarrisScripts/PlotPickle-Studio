#!/usr/bin/env python3
"""On-demand, read-only PlotPickle Radar report locator. No dependencies or tokens.

Prints only dates, the canonical GitHub source URL and bounded report text. Uses
PUBLIC GitHub APIs; network restrictions or rate limits fail visibly. The
`--input` option accepts a downloaded GitHub issue search+comments bundle.
Never executes research content, installs packages, writes projects or schedules.
"""
import argparse
import datetime as dt
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

REPO = "BryanHarrisScripts/PlotPickle"
BASE = "https://api.github.com"
MARKER = re.compile(r"<!-- PLOTPICKLE-OSS-RADAR-DAY:(\d{4}-\d{2}-\d{2}) -->")
TITLE = re.compile(r"^\[OSS RADAR\] [A-Z][a-z]+ 20\d{2}$")
MAX_BYTES = 5_000_000


def get_json(path):
    req = urllib.request.Request(BASE + path, headers={"Accept":"application/vnd.github+json", "User-Agent":"PlotPickle-Plugin-Radar-ReadOnly", "X-GitHub-Api-Version":"2022-11-28"})
    with urllib.request.urlopen(req, timeout=15) as response:
        data = response.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError("oversize GitHub response")
    return json.loads(data)


def fetch_bundle():
    query = urllib.parse.quote('repo:' + REPO + ' in:title "[OSS RADAR]"')
    issues = get_json('/search/issues?q=' + query + '&sort=updated&order=desc&per_page=20').get('items', [])
    issues = [i for i in issues if TITLE.fullmatch(str(i.get('title', ''))) and i.get('repository_url', '').endswith('/' + REPO) and not i.get('pull_request')]
    for issue in issues[:3]:
        number = int(issue['number'])
        comments = get_json('/repos/' + REPO + '/issues/' + str(number) + '/comments?per_page=100')
        if not isinstance(comments, list):
            raise ValueError('invalid comments response')
        yield issue, comments


def latest_from_bundles(bundles, now=None):
    today = now or dt.datetime.now(dt.timezone.utc).date()
    matches = []
    for issue, comments in bundles:
        if not TITLE.fullmatch(str(issue.get('title', ''))):
            continue
        if issue.get('html_url', '').split('#')[0] != 'https://github.com/' + REPO + '/issues/' + str(issue.get('number')):
            continue
        for comment in comments:
            body = str(comment.get('body') or '')
            marker = MARKER.search(body)
            if not marker:
                continue
            try:
                day = dt.date.fromisoformat(marker.group(1))
            except ValueError:
                continue
            if day > today or ('## OSS Radar — ' + day.isoformat()) not in body:
                continue
            url = comment.get('html_url') or comment.get('url') or ''
            if not str(url).startswith('https://github.com/' + REPO + '/issues/' + str(issue['number']) + '#issuecomment-'):
                continue
            matches.append((day, issue['number'], url, body))
    if not matches:
        return {'status':'unavailable','sourceRepository':REPO, 'reason':'no valid dated report comment in retrieved issue threads'}
    day, number, url, body = max(matches, key=lambda x:(x[0], x[2]))
    age = (today - day).days
    return {'status':'available', 'sourceRepository':REPO, 'reportDate':day.isoformat(),
            'ageDays':age,'freshToday':age == 0,'issueUrl':'https://github.com/' + REPO + '/issues/' + str(number),
            'reportUrl':url, 'reportBody':body, 'workflowHealth':'not-checked',
            'adoptionAuthority':'RESEARCH_ONLY / HUMAN_REVIEW_REQUIRED'}


def main(argv=None):
    p=argparse.ArgumentParser(description='Read original PlotPickle OSS Radar public report, no credentials, no writes.')
    p.add_argument('--input',help='offline JSON fixture containing [{"issue":..., "comments":[...]}]')
    p.add_argument('--today',help='UTC date YYYY-MM-DD (testing/report reproducibility)')
    p.add_argument('--max-chars',type=int,default=16000)
    args=p.parse_args(argv)
    try:
        day=dt.date.fromisoformat(args.today) if args.today else None
        if args.input:
            with open(args.input, encoding='utf-8') as f: data=json.load(f)
            if not isinstance(data,list): raise ValueError('input must be a list of issue/comment bundles')
            bundles=[(x['issue'], x['comments']) for x in data]
        else:
            bundles=list(fetch_bundle())
        result=latest_from_bundles(bundles,now=day)
        if 'reportBody' in result:
            limit=min(100000,max(1000,args.max_chars))
            body=result.pop('reportBody')
            result['reportExcerpt']=body[:limit]
            result['excerptTruncated']=len(body)>limit
        print(json.dumps(result,ensure_ascii=False,indent=2))
        return 0 if result['status']=='available' else 2
    except (ValueError, KeyError, TypeError, OSError, urllib.error.URLError) as exc:
        print(json.dumps({'status':'unavailable','sourceRepository':REPO,'reason':type(exc).__name__ + ': ' + str(exc)[:220], 'workflowHealth':'not-checked'},indent=2))
        return 2


if __name__=='__main__':
    sys.exit(main())
