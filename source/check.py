"""Check local links, profile publication boundaries, and ignored input paths."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import json
import html
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
profile = json.loads((ROOT/'source/profile.json').read_text(encoding='utf-8'))
assert 'review_notes' not in profile, 'Internal notes must not be published'
assert all('paper_source' not in m and 'video_source' not in m for m in profile['manuscripts'])

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.paths = []
        self.videos = 0
        self.ids = set()
    def handle_starttag(self, tag, attrs):
        if tag == 'video':
            self.videos += 1
        for key, value in attrs:
            if key == 'id':
                self.ids.add(value)
            if key in ('href', 'src', 'poster') and value:
                self.paths.append(value)

for relative in ('index.html', 'research/index.html', 'research/myomimetic-exosuit/index.html'):
    page = ROOT/relative
    text = page.read_text(encoding='utf-8')
    parser = Links()
    parser.feed(text)
    assert parser.videos == (0 if relative == 'index.html' else 1), f'Unexpected video layout in {relative}'
    assert text.count('aria-current="page"') == 1, f'Missing active navigation in {relative}'
    assert 'class="brand"' not in text, f'Duplicate name in navigation: {relative}'
    if relative == 'index.html':
        assert 'href="research/index.html#myomimetic-video">Video</a>' in text
        assert html.escape(profile['homepage_interest_statement'],quote=True) in text.replace('<br class="sentence-break">', ' ')
        assert html.escape(profile['homepage_goal_statement'],quote=True) in text
        assert 'id="background"' in text
        assert {'education', 'experience', 'awards'} <= parser.ids
        assert text.count('class="entry background-entry"') == sum(len(profile[k]) for k in ('education','experience','awards'))
    assert 'myomimetic-exosuit-draft.pdf' not in text, 'Draft link must stay removed'
    for url in parser.paths:
        parts = urlsplit(url)
        if parts.scheme or parts.netloc or not parts.path:
            continue
        target = (page.parent/unquote(parts.path)).resolve()
        assert target.is_relative_to(ROOT), f'Link leaves repository: {url}'
        assert target.exists(), f'Missing local link: {relative}: {url}'
        if parts.fragment and target.suffix == '.html':
            linked = Links()
            linked.feed(target.read_text(encoding='utf-8'))
            assert unquote(parts.fragment) in linked.ids, f'Missing link target: {url}'

probes = ['inbox/notes/request.md', 'inbox/research/manuscript.pdf',
          'inbox/photos/portrait.jpg', 'inbox/education/transcript.pdf',
          'inbox/references/example.docx', 'inbox/awards/certificate.png',
          '_build/check.txt', 'output/package.zip']
ignored = subprocess.check_output(['git', 'check-ignore', '--no-index', *probes],
                                  cwd=ROOT, text=True).splitlines()
assert set(probes) == set(ignored), 'A local input/build path is not ignored'
tracked = subprocess.check_output(['git', 'ls-files'], cwd=ROOT, text=True).splitlines()
for path in tracked:
    if path.startswith('inbox/'):
        assert path == 'inbox/README.md' or path.endswith('/.gitkeep'), f'Raw input tracked: {path}'
    assert not path.startswith(('_build/', 'output/')), f'Build output tracked: {path}'
    assert not ('draft' in path.lower() and path.lower().endswith('.pdf')), path

archive = ROOT/'output/godongdongmin.github.io.zip'
if archive.exists():
    with zipfile.ZipFile(archive) as z:
        assert not any(p.startswith(('inbox/', 'source/', '_build/', '.git/')) for p in z.namelist())
        assert not any('draft.pdf' in p for p in z.namelist())
        assert z.read('files/Dongmin_Go_CV.pdf') == (ROOT/'files/Dongmin_Go_CV.pdf').read_bytes()
assert (ROOT/'files/Dongmin_Go_CV.pdf').read_bytes().startswith(b'%PDF-')
print('OK: Home/Research pages, video links, public data, ignored inputs, and deployment package.')
