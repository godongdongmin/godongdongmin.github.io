"""Read-only checks against the deployed academic homepage."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import hashlib
import html
import json

BASE=Path(__file__).resolve().parents[1]
ORIGIN='https://godongdongmin.github.io/'
TARGETS=[('', 'GET'),('research/', 'GET'),('research/myomimetic-exosuit/', 'GET'),
         ('files/Dongmin_Go_CV.pdf','GET'),('files/myomimetic-exosuit-draft.pdf','HEAD'),
         ('files/myomimetic-exosuit-video.mp4','HEAD'),('assets/style.css','HEAD'),
         ('assets/portrait.jpg','HEAD'),('assets/myomimetic-poster.jpg','HEAD')]
def check(item):
    path,method=item
    request=Request(ORIGIN+path,method=method,headers={'User-Agent':'AcademicHomepageDeploymentCheck/1.0'})
    if path=='files/myomimetic-exosuit-draft.pdf':
        try:
            with urlopen(request,timeout=25) as response:
                raise AssertionError('Removed draft is still publicly served')
        except HTTPError as error:
            assert error.code==404, f'Unexpected draft URL status: {error.code}'
            return {'url':ORIGIN+path,'status':404,'draft_removed':True}
    with urlopen(request,timeout=25) as response:
        report={'url':response.url,'status':response.status,'content_type':response.headers.get('Content-Type'),'content_length':response.headers.get('Content-Length')}
        body=response.read() if method=='GET' else b''
    if path=='':
        text=body.decode('utf-8')
        assert all(s in text for s in ['Dongmin Go','HUROTICS','4.37 / 4.50','3.82 / 4.50','Mar. 2026 - Present']), 'Deployed homepage content does not match'
        profile=json.loads((BASE/'source/profile.json').read_text(encoding='utf-8'))
        assert all(p['title'] in text for p in profile['publications']), 'Published works are missing'
        assert 'Work in progress; not yet submitted' in text and 'Manuscripts in Preparation' not in text, 'Pending manuscript format does not match'
        assert all(html.escape(m.get('relation',''),quote=True) in text for m in profile['manuscripts']), 'Thesis-to-journal relationship is missing'
        report['latest_profile_verified']=True
        report['publications_verified']=True
        assert '<video ' not in text and 'research/index.html#myomimetic-video' in text, 'Home video link does not match'
        prose = text.replace('<br class="sentence-break">', ' ').replace('<strong>', '').replace('</strong>', '')
        assert html.escape(profile['homepage_interest_statement'],quote=True) in prose
        assert html.escape(profile['homepage_goal_statement'],quote=True) in prose
        assert html.escape(profile['summary'],quote=True) in prose
        assert 'class="background-grid"' in text
        assert all(f'id="{section}"' in text for section in ('education', 'experience', 'awards'))
        assert 'href="index.html" aria-current="page">Home</a>' in text
        assert 'Paper (draft)' not in text and 'myomimetic-exosuit-draft.pdf' not in text
        report['home_navigation_and_video_link_verified']=True
    if path=='research/':
        text=body.decode('utf-8')
        assert 'id="myomimetic-video"' in text and '<video ' in text
        assert 'href="index.html" aria-current="page">Research</a>' in text
        report['research_page_and_active_navigation_verified']=True
    if path=='research/myomimetic-exosuit/':
        text=body.decode('utf-8')
        assert '<video ' in text and 'myomimetic-exosuit-video.mp4' in text
        assert 'myomimetic-exosuit-draft.pdf' not in text
        profile=json.loads((BASE/'source/profile.json').read_text(encoding='utf-8'))
        assert all(html.escape(m.get('thesis_title',''),quote=True) in text for m in profile['manuscripts']), 'Project thesis context is missing'
        report['research_and_video_link_verified']=True
    if path=='files/Dongmin_Go_CV.pdf':
        assert body==(BASE/'files/Dongmin_Go_CV.pdf').read_bytes(), 'Live CV differs from local version'
        report['latest_cv_sha256']=hashlib.sha256(body).hexdigest()
    return report
with ThreadPoolExecutor(max_workers=4) as pool:
    reports=list(pool.map(check,TARGETS))
(BASE/'_build').mkdir(exist_ok=True)
(BASE/'_build/live-check.json').write_text(json.dumps(reports,indent=2),encoding='utf-8')
print(json.dumps(reports,indent=2))
