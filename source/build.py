"""Build the CV (XeLaTeX) and static academic website from profile.json.

Usage (from the repository root): python source/build.py [--site-only]
Requires Python 3 and XeLaTeX; uses the Python standard library only.
"""
from pathlib import Path
import html
import json
import shutil
import subprocess
import sys
import zipfile
from research_page import build_research_page, build_research_index, site_navigation, RESEARCH_FIGURES

BASE = Path(__file__).resolve().parents[1]
SOURCE = BASE / 'source'
BUILD = BASE / '_build'
SITE = BASE
OUTPUT = BASE / 'output'
P = json.loads((SOURCE / 'profile.json').read_text(encoding='utf-8'))
if 'review_notes' in P:
    raise SystemExit('Keep private review notes in inbox/, not in the public profile.json.')
if '--site-only' not in sys.argv and not shutil.which('xelatex'):
    raise SystemExit('XeLaTeX is required for the CV. Install TeX Live or use --site-only for HTML updates.')
for folder in (BUILD, SITE / 'assets', SITE / 'files', OUTPUT):
    folder.mkdir(parents=True, exist_ok=True)

def h(value):
    return html.escape(str(value), quote=True)

def tex(value):
    substitutions = {'\\':r'\textbackslash{}','&':r'\&','%':r'\%','$':r'\$','#':r'\#','_':r'\_','{':r'\{','}':r'\}','~':r'\textasciitilde{}','^':r'\textasciicircum{}'}
    return ''.join(substitutions.get(ch,ch) for ch in str(value))

icons = {
    'github':'<path d="M12 .9a11.1 11.1 0 0 0-3.51 21.63c.55.1.76-.24.76-.54v-2.07c-3.1.67-3.76-1.32-3.76-1.32-.51-1.29-1.24-1.63-1.24-1.63-1.01-.69.08-.68.08-.68 1.12.08 1.71 1.15 1.71 1.15.99 1.69 2.6 1.2 3.24.92.1-.72.39-1.2.7-1.48-2.47-.28-5.07-1.24-5.07-5.49 0-1.21.43-2.2 1.14-2.98-.11-.28-.5-1.41.11-2.94 0 0 .94-.3 3.06 1.14a10.6 10.6 0 0 1 5.57 0c2.13-1.44 3.06-1.14 3.06-1.14.61 1.53.23 2.66.11 2.94.71.78 1.14 1.77 1.14 2.98 0 4.26-2.6 5.2-5.08 5.48.4.35.76 1.03.76 2.07v3.05c0 .3.2.65.76.54A11.1 11.1 0 0 0 12 .9Z"/>',
    'email':'<path d="M3 4h18a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2Zm9 9L3 7v11h18V7l-9 6Zm0-2 8-5H4l8 5Z"/>',
    'document':'<path d="M5 2h9l5 5v15H5V2Zm2 2v16h10V8h-4V4H7Zm2 7h6v2H9v-2Zm0 4h6v2H9v-2Z"/>'
}
def icon(name):
    return f'<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">{icons[name]}</svg>'

def detail_list(details):
    return '<ul>' + ''.join(f'<li>{h(s)}</li>' for s in details) + '</ul>' if details else ''

def section(name, body, ident=None):
    return f'<section class="section" id="{ident or name.lower()}"><h2>{h(name)}</h2>{body}</section>'

def background_entry(title, subtitle, dates, details):
    detail_text = ''.join(f'<p class="detail">{h(d)}</p>' for d in details)
    return f'<article class="entry background-entry"><h3>{h(title)}</h3><p>{h(subtitle)}</p>{detail_text}<p class="background-date">{h(dates)}</p></article>'

# Keep each category separate, in the latest-first order stored in profile.json.
education = ''.join(background_entry(e['institution'], e['degree'], e['dates'], e['details']) for e in P['education'])
experience = ''.join(background_entry(e['institution'], e.get('homepage_role', e['role']), e['dates'], e['details']) for e in P['experience'])
awards = ''.join(background_entry(a['title'], a['event'], a['date'], [a['organization']]) for a in P['awards'])
background = '<div class="background-grid" id="background">' + section('Education', education, 'education') + '<div class="background-right">' + section('Experience', experience, 'experience') + section('Honors & Awards', awards, 'awards') + '</div></div>'
publications = ''
for pub in P['publications']:
    title = h(pub['title'])
    if pub.get('url'):
        title = f'<a href="{h(pub["url"])}">{title}</a>'
    links = ''.join(f'<a href="{h(url)}">{h(label)}</a>' for label,url in pub.get('links',{}).items())
    authors = h(pub['authors']).replace(h(P['name']), '<strong>'+h(P['name'])+'</strong>')
    publications += f'<article class="entry"><h3 class="publication-title">[{h(pub["label"])}] {title}</h3><p>{authors}</p><p class="detail">{h(pub["venue"])} · {h(pub["citation_details"])}</p><div class="publication-links">{links}</div></article>'
projects = ''.join(f'<article class="entry"><h3>{h(p["title"])}</h3><p>{h(p["description"])}</p>'+detail_list(p.get('details',[]))+(f'<p><a href="{h(p["url"])}">Project / Code</a></p>' if p.get('url') else '')+'</article>' for p in P['projects'])
manuscripts = ''
for m in P.get('manuscripts',[]):
    authors = h(m.get('authors','')).replace(h(P['name']),'<strong>'+h(P['name'])+'</strong>')
    title = f'<a href="{h(m["url"])}">{h(m["title"])}</a>' if m.get('url') else h(m['title'])
    video = '<div class="publication-links"><a href="research/index.html#myomimetic-video">Video</a></div>' if m.get('video_url') else ''
    manuscripts += f'<article class="entry" id="manuscripts"><h3 class="publication-title">[{h(m["label"])}] {title}</h3><p class="authors">{authors}</p><p class="detail">{h(m.get("relation",""))} <em>{h(m["status"])}</em></p>{video}</article>'
cv_filename = 'Dongmin_Go_CV.pdf'
email_link = f'<a href="mailto:{h(P["email"])}">{icon("email")}{h(P["email"])}</a>' if P['email'] else ''
interest_sentence = P.get('homepage_interest_statement','')
native_name = f'<span class="native-name" lang="ko">{h(P["name_ko"])}</span>' if P.get('name_ko') else ''
intro = f'<section class="section intro" id="about"><h2>About Me</h2><p>{h(P["summary"])} {h(interest_sentence)}</p><p>{h(P.get("background",""))}</p><a class="cv-link" href="files/{cv_filename}">{icon("document")}Curriculum Vitae <span aria-hidden="true">↗</span></a></section>'
publication_legend = '<p class="detail">J = Journal · C = Conference · T = Thesis · W = Work in progress</p>'
content = intro + (section('Publications',publication_legend+publications+manuscripts) if publications or manuscripts else '') + (section('Research Projects',projects,'projects') if projects else '') + background
page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{h(P['name'])} | Academic Homepage</title><meta name="description" content="{h(P['name'])} at HUROTICS. M.S. in Mechanical Engineering, Chung-Ang University; former EUV Equipment Engineer at Samsung Electronics DS.">
<meta name="theme-color" content="#ffffff"><link rel="canonical" href="{h(P['website'])}"><meta property="og:title" content="{h(P['name'])} | Academic Homepage"><meta property="og:description" content="{h(P['headline'])}. Education, experience, and research."><meta property="og:type" content="website"><meta property="og:url" content="{h(P['website'])}"><meta property="og:image" content="{h(P['website'])}assets/portrait.jpg"><link rel="icon" href="assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="assets/style.css"></head>
<body><a class="skip" href="#main">Skip to content</a>{site_navigation('home','index.html','research/index.html')}
<div class="layout"><aside class="profile" aria-label="Profile"><img class="portrait" src="assets/portrait.jpg" alt="Portrait of {h(P['name'])}" width="218" height="262"><h1>{h(P['name'])}{native_name}</h1><p class="headline">{h(P['headline'])}</p><p class="affiliation">{h(P.get('profile_affiliation','Chung-Ang University'))}</p><div class="profile-links">{email_link}<a href="https://github.com/{h(P['github'])}">{icon('github')}GitHub</a><a href="files/{cv_filename}">{icon('document')}Curriculum Vitae</a></div></aside><main class="content" id="main">{content}</main></div>
<footer class="footer"><span>© 2026 {h(P['name'])}</span><span>Last updated: {h(P['updated'])} · <a href="https://github.com/{h(P['github'])}">GitHub</a></span></footer></body></html>'''
(SITE/'index.html').write_text(page,encoding='utf-8')
# The published portrait is the maintained asset; uploaded reference folders
# are not build inputs and may be removed after their information is recorded.
if not (SITE/'assets/portrait.jpg').is_file():
    raise FileNotFoundError('Missing assets/portrait.jpg. Restore this tracked asset from Git.')
(SITE/'assets/favicon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="12" fill="#185a9d"/><text x="32" y="43" text-anchor="middle" fill="white" font-family="Georgia,serif" font-size="34">D</text></svg>',encoding='utf-8')
(SITE/'.nojekyll').write_text('',encoding='utf-8')
for m in P.get('manuscripts',[]):
    if m.get('video_url'):
        build_research_page(SITE,P,m)
build_research_index(SITE,P)

def package_site():
    # Explicit deployment files only: never package inbox/, source/, or build output.
    deploy_files = ['index.html', '.nojekyll', 'assets/style.css',
                    'assets/portrait.jpg', 'assets/favicon.svg',
                    'assets/myomimetic-poster.jpg', 'files/Dongmin_Go_CV.pdf',
                    'files/myomimetic-exosuit-video.mp4',
                    'research/myomimetic-exosuit/index.html', 'research/index.html']
    deploy_files += [f'assets/myomimetic-exosuit/{name}.png' for name in RESEARCH_FIGURES]
    with zipfile.ZipFile(OUTPUT/'godongdongmin.github.io.zip','w',zipfile.ZIP_DEFLATED) as archive:
        for relative in deploy_files:
            archive.write(SITE/relative,relative)

if '--site-only' in sys.argv:
    package_site()
    print('Built site and deployment ZIP; existing CV unchanged.')
    raise SystemExit(0)

contact = [r'\href{https://github.com/'+tex(P['github'])+'}{GitHub: '+tex(P['github'])+'}']
if P['email']:
    contact.insert(0,r'\href{mailto:'+tex(P['email'])+'}{'+tex(P['email'])+'}')
contact.append(r'\href{'+tex(P['website'])+'}{'+tex(P['website'].removeprefix('https://').rstrip('/'))+'}')
chunks = [r'''\documentclass[11pt,a4paper]{article}
\usepackage[top=17mm,bottom=17mm,left=16mm,right=16mm]{geometry}
\usepackage{fontspec}
\IfFontExistsTF{Times New Roman}{\setmainfont{Times New Roman}}{\setmainfont{TeX Gyre Termes}}
\usepackage[dvipsnames]{xcolor}
\usepackage{hyperref}
\usepackage{enumitem}
\usepackage{titlesec}
\usepackage{tabularx}
\usepackage{needspace}
\hypersetup{colorlinks=true,urlcolor=MidnightBlue,linkcolor=MidnightBlue,pdfauthor={'''+tex(P['name'])+r'''},pdftitle={'''+tex(P['name'])+r''' - Curriculum Vitae}}
\pagestyle{empty}
\setlength{\parindent}{0pt}
\setlength{\parskip}{0pt}
\setlength{\tabcolsep}{0pt}
\titleformat{\section}{\large\scshape\bfseries}{}{0pt}{}[\vspace{2pt}\titlerule]
\titlespacing*{\section}{0pt}{12pt}{8pt}
\setlist[itemize]{leftmargin=14pt,itemsep=2pt,topsep=3pt,parsep=0pt}
\newcommand{\entry}[3]{\needspace{4\baselineskip}\begin{tabularx}{\linewidth}{@{}X r@{}}\textbf{#1}&\textit{#2}\\\end{tabularx}\if\relax\detokenize{#3}\relax\par\else\vspace{-2pt}\\\textit{#3}\par\fi}
\begin{document}
\begin{center}
{\fontsize{27}{32}\selectfont\bfseries '''+tex(P['name'])+r'''}\\[7pt]
'''+r' \enspace | \enspace '.join(contact)+r'''
\end{center}
\vspace{1pt}
''']
def tex_details(details):
    return '\\begin{itemize}\n'+''.join('\\item '+tex(d)+'\n' for d in details)+'\\end{itemize}\n' if details else ''
chunks.append(r'\section{Experience}'+'\n')
for e in P['experience']:
    chunks.append(r'\entry{'+tex(e['institution'])+'}{'+tex(e['dates'])+'}{'+tex(e['role'])+'}\n'+tex_details(e['details'])+r'\vspace{4pt}'+'\n')
chunks.append(r'\section{Education}'+'\n')
for e in P['education']:
    chunks.append(r'\entry{'+tex(e['institution'])+'}{'+tex(e['dates'])+'}{'+tex(e['degree'])+'}\n'+tex_details(e['details'])+r'\vspace{4pt}'+'\n')
if P['publications'] or P.get('manuscripts'):
    chunks.append(r'\section{Publications}'+'\n')
    chunks.append(r'{\small\itshape J = Journal, C = Conference, T = Thesis, W = Work in progress}\par\vspace{6pt}'+'\n')
    chunks.append(r'\begin{description}[leftmargin=32pt,labelwidth=28pt,labelsep=4pt,font=\normalfont,itemsep=7pt,parsep=0pt,topsep=0pt]'+'\n')
    for i,pub in enumerate(P['publications'],1):
        title = r'\textbf{'+tex(pub['title'])+'}'
        if pub.get('url'):
            title=r'\href{'+tex(pub['url'])+'}{'+title+'}'
        authors = tex(pub['authors']).replace(tex(P['name']),r'\textbf{'+tex(P['name'])+'}')
        chunks.append(r'\item[{['+tex(pub['label'])+']}] '+authors+'. '+title+'. '+r'\textit{'+tex(pub['venue'])+'}, '+tex(pub['citation_details'])+'.\n')
    for manuscript in P.get('manuscripts',[]):
        authors = tex(manuscript['authors']).replace(tex(P['name']),r'\textbf{'+tex(P['name'])+'}')
        chunks.append(r'\item[{['+tex(manuscript['label'])+']}] '+authors+'. '+r'\textbf{'+tex(manuscript['title'])+'}. '+tex(manuscript.get('relation',''))+' '+r'\textit{'+tex(manuscript['status'])+'}.\n')
    chunks.append(r'\end{description}'+'\n')
if P['projects']:
    chunks.append(r'\section{Research Projects}'+'\n')
    for project in P['projects']:
        chunks.append(r'\textbf{'+tex(project['title'])+r'}\par '+tex(project['description'])+'\n'+tex_details(project.get('details',[]))+r'\vspace{7pt}'+'\n')
chunks.append(r'\section{Honors and Awards}'+'\n')
for a in P['awards']:
    chunks.append(r'\entry{'+tex(a['title'])+'}{'+tex(a['date'])+'}{'+tex(a['event'])+'}\n'+tex(a['organization'])+r'\par\vspace{6pt}'+'\n')
if P['skills'] or P['research_interests'] or P['languages']:
    chunks.append(r'\section{Additional Information}'+'\n')
    for label,items in [('Research interests',P['research_interests']),('Technical skills',P['skills']),('Languages',P['languages'])]:
        if items:
            chunks.append(r'\textbf{'+label+':} '+tex('; '.join(items))+r'\par\vspace{4pt}'+'\n')
chunks.append(r'\end{document}'+'\n')
tex_path = BUILD/'Dongmin_Go_CV.tex'
tex_path.write_text(''.join(chunks),encoding='utf-8')
logs = []
for _ in range(2):
    result = subprocess.run(['xelatex','-interaction=nonstopmode','-halt-on-error',f'-output-directory={BUILD}',str(tex_path)],cwd=BASE,capture_output=True,text=True,encoding='utf-8',errors='replace')
    logs.append(result.stdout+'\n'+result.stderr)
    (BUILD/'latex-build.log').write_text('\n'.join(logs),encoding='utf-8')
    if result.returncode:
        raise SystemExit('XeLaTeX failed; see _build/latex-build.log')
for target in (OUTPUT/cv_filename,SITE/'files'/cv_filename):
    shutil.copyfile(BUILD/cv_filename,target)
package_site()
print('Built CV: '+str(OUTPUT/cv_filename))
print('Built site: '+str(SITE/'index.html'))
