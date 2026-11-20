"""Static project page for the supplied manuscript and supplementary video."""
from html import escape as h
from hashlib import sha256

def stylesheet_href(site, prefix):
    # A new URL when styles change prevents stale CSS after a Pages deployment.
    version = sha256((site/'assets/style.css').read_bytes()).hexdigest()[:12]
    return f'{prefix}assets/style.css?v={version}'

RESEARCH_FIGURES = {
    'system': (2000, 794),
    'networks': (2000, 930),
    'setup': (2000, 1275),
    'critic_ablation_1col': (1531, 2000),
    'layer2_effort_1col': (2000, 1881),
    'layer3_GM_1col': (1787, 2000),
    'sim_effort_1col': (2000, 1626),
    'layer3_scatter_1col': (1726, 2000),
}

def research_figure(name, alt, caption, compact=False):
    width, height = RESEARCH_FIGURES[name]
    src = f'../../assets/myomimetic-exosuit/{name}.png'
    classes = 'study-figure figure-compact' if compact else 'study-figure'
    return f'<figure class="{classes}"><a href="{src}" target="_blank" rel="noopener" aria-label="{h(alt)} — open full-size image"><img src="{src}" alt="{h(alt)}" width="{width}" height="{height}" decoding="async"></a><figcaption>{h(caption)}</figcaption></figure>'

def site_navigation(active, home_url, research_url):
    links = ''.join(
        f'<a href="{h(url)}"'+(' aria-current="page"' if key == active else '')+f'>{label}</a>'
        for key, label, url in [('home','Home',home_url),('research','Research',research_url)]
    )
    return f'<header class="topbar"><nav class="nav site-nav" aria-label="Main navigation"><div class="nav-links">{links}</div></nav></header>'

def build_selected_project(site, profile, project):
    dest = site/project['url']
    dest.parent.mkdir(parents=True, exist_ok=True)
    contributions = ''.join(f'<li>{h(detail)}</li>' for detail in project['details'])
    videos = ''
    for video in project['videos']:
        portrait = ' ces-video-portrait' if video['portrait'] else ''
        videos += f'''<figure class="ces-demo" id="{h(video['id'])}"><h3>{h(video['title'])}</h3><video class="project-video{portrait}" controls playsinline preload="metadata" poster="../../{h(video['poster'])}" aria-label="{h(video['title'])}" aria-describedby="{h(video['id'])}-caption"><source src="../../{h(video['url'])}" type="video/mp4">Your browser does not support embedded video. <a href="../../{h(video['url'])}">Download the video</a>.</video><figcaption class="media-caption" id="{h(video['id'])}-caption">{h(video['caption'])}</figcaption></figure>'''
    page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{h(project['title'])} | {h(profile['name'])}</title><meta name="description" content="{h(project['description'])}">
<link rel="stylesheet" href="{stylesheet_href(site, '../../')}"><link rel="icon" href="../../assets/favicon.svg" type="image/svg+xml"><link rel="canonical" href="{h(profile['website']+project['url'])}">
<meta property="og:title" content="{h(project['title'])}"><meta property="og:description" content="{h(project['description'])}"><meta property="og:image" content="{h(profile['website']+project['thumbnail'])}"><meta property="og:type" content="website">
</head><body class="project-page"><a class="skip" href="#main">Skip to content</a>{site_navigation('home','../../index.html','../../research/index.html')}
<main class="project-main ces-main" id="main"><p class="project-back"><a href="../../index.html#projects">← Selected Projects</a></p><header class="project-header"><p class="eyebrow">SELECTED PROJECT · CES 2025</p><h1>{h(project['title'])}</h1><p class="project-authors">{h(project['role'])}</p></header>
<section class="section ces-overview" aria-labelledby="overview-heading"><figure class="ces-photo"><a href="../../{h(project['thumbnail'])}"><img src="../../{h(project['thumbnail'])}" alt="{h(project['photo_alt'])}" width="1080" height="1472"></a><figcaption class="media-caption">H-MEDI demonstration at CES 2025.</figcaption></figure><div><h2 id="overview-heading">From algorithm to live demonstration</h2><p>{h(project['description'])}</p><h3>My contributions</h3><ul class="ces-contributions">{contributions}</ul><p class="section-note">The high-level controller recognized motion-state changes and generated target assistance forces appropriate to the current activity.</p></div></section>
<section class="section" id="demonstrations"><h2>Demonstrations</h2><p>On-site footage of sitting, standing, and walking with the H-MEDI wearable robot.</p><div class="ces-demos">{videos}</div></section>
</main><footer class="footer"><a href="../../index.html#projects">← Selected Projects</a><span>{h(profile['name'])} · {h(profile['updated'])}</span></footer></body></html>'''
    dest.write_text(page, encoding='utf-8')


def build_research_index(site, profile):
    dest = site/'research'
    dest.mkdir(parents=True, exist_ok=True)
    studies = ''
    for m in profile.get('manuscripts', []):
        authors = h(m['authors']).replace(h(profile['name']),'<strong>'+h(profile['name'])+'</strong>')
        details = '../'+m['url']
        video = f'<video id="myomimetic-video" class="project-video" controls playsinline preload="metadata" poster="../{h(m["thumbnail"])}" aria-label="Research video: {h(m["title"])}"><source src="../{h(m["video_url"])}" type="video/mp4">Your browser does not support embedded video.</video>' if m.get('video_url') else ''
        studies += f'''<article class="research-study"><p class="eyebrow">SUBMITTED MANUSCRIPT</p><h2><a href="{h(details)}">{h(m['title'])}</a></h2><p class="authors">{authors}</p><p class="section-note">{h(m.get('relation',''))} {h(m['status'])}.</p><p class="study-summary">{h(m.get('description',''))}</p>{video}<p class="study-more"><a href="{h(details)}">Study details <span aria-hidden="true">→</span></a></p></article>'''
    published = ''
    for p in profile['publications']:
        if not p['label'].startswith(('J.','C.')):
            continue
        published += f'<article class="entry"><h3><a href="{h(p["url"])}">{h(p["title"])}</a></h3><p>{h(p["authors"])}</p><p class="detail">{h(p["venue"])} · {h(p["citation_details"])}</p></article>'
    page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Research | {h(profile['name'])}</title><meta name="description" content="Research projects, videos, and publications by {h(profile['name'])}.">
<link rel="stylesheet" href="{stylesheet_href(site, '../')}"><link rel="icon" href="../assets/favicon.svg" type="image/svg+xml"><link rel="canonical" href="{h(profile['website'])}research/"></head>
<body><a class="skip" href="#main">Skip to content</a>{site_navigation('research','../index.html','index.html')}
<main class="research-main" id="main"><header class="research-heading"><h1>Research</h1><p>{h(', '.join(profile.get('homepage_interests',[])))}</p></header>{studies}<section class="section published-research"><h2>Published Work</h2>{published}</section></main>
<footer class="footer"><span>© 2026 {h(profile['name'])}</span><span>Last updated: {h(profile['updated'])}</span></footer></body></html>'''
    (dest/'index.html').write_text(page,encoding='utf-8')

def build_research_page(site, profile, manuscript):
    dest = site/'research/myomimetic-exosuit'
    dest.mkdir(parents=True, exist_ok=True)
    authors = h(manuscript['authors']).replace(h(profile['name']),'<strong>'+h(profile['name'])+'</strong>')
    thesis_note = f'<p class="section-note">This journal manuscript extends Dongmin Go\'s master\'s thesis, <em>{h(manuscript["thesis_title"])}</em> (Chung-Ang University, 2025).</p>' if manuscript.get('thesis_title') else ''
    page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{h(manuscript['title'])} | {h(profile['name'])}</title>
<meta name="description" content="{h(manuscript['description'])}">
<link rel="stylesheet" href="{stylesheet_href(site, '../../')}"><link rel="icon" href="../../assets/favicon.svg" type="image/svg+xml">
<link rel="canonical" href="{h(profile['website'])}research/myomimetic-exosuit/">
</head><body class="project-page"><a class="skip" href="#main">Skip to content</a>
{site_navigation('research','../../index.html','../index.html')}
<main class="project-main" id="main"><header class="project-header"><p class="eyebrow">SUBMITTED MANUSCRIPT</p><h1>{h(manuscript['title'])}</h1><p class="project-authors">{authors}</p><p class="project-affiliations">Chung-Ang University · HUROTICS</p><p class="section-note">{h(manuscript['status'])}.</p></header>
<section class="section" id="overview"><h2>Overview</h2>{thesis_note}<p>This study tests whether modeling a wearer’s goal of unloading the assisted muscles as a shared human–exosuit reward brings simulated muscle responses closer to measured responses. Human and exosuit policies learn together under a unified critic, and the exosuit policy is deployed without further learning for comparison with surface EMG from seven participants.</p><p>The framework covers level walking, incline walking, and stair ascent without reference-motion tracking. On hardware, the controller uses IMU and past-action histories, without requiring terrain labels or muscle-state measurements.</p>
{research_figure('system', 'System overview linking coupled musculoskeletal simulation to exosuit deployment across level walking, incline walking, and stair ascent.', 'System overview. Muscle and exosuit policies learn together in simulation; the exosuit policy is then deployed and evaluated across three terrains.')}
<p class="figure-hint">Select any figure to view it at full resolution.</p>
<div class="method-grid"><article><h3>Shared muscle objective</h3><p>BASE includes aggregate muscle-effort reduction. TGT adds an assisted-muscle unloading term to the shared reward used by the human and exosuit policies.</p></article><article><h3>Embedded control</h3><p>Policy inference at a nominal 50 Hz on a Jetson Orin Nano. Force commands travel over CAN to the robot's 1 kHz low-level controller.</p></article><article><h3>Hardware evaluation</h3><p>Two reward variants, BASE and TGT, are compared with motor-off assistance in seven healthy participants across three environments.</p></article></div></section>
<section class="section" id="architecture"><h2>Network Architecture</h2><p>The muscle and exosuit policies share a unified critic during training. The exosuit policy combines long and short histories of IMU observations and past actions, and the same policy is shared between the left and right sides.</p>
{research_figure('networks', 'Muscle policy, unified critic, and shared bilateral exosuit policy with a dual-history encoder and hardware deployment pathway.', 'Network architecture. The exosuit policy uses 2 s and 80 ms histories; only this policy is transferred to hardware, followed by filtering and force scaling.')}</section>
<section class="section" id="experimental-setup"><h2>Experimental Setup</h2><p>The wearable system combines an onboard inference computer, inertial sensors, and force sensing. EMG electrodes record activity from seven lower-limb muscles during the hardware evaluation.</p>
{research_figure('setup', 'Exosuit hardware configuration and EMG electrode placement for GM, RF, VL, BF, TA, MG, and SOL.', 'Experimental setup. Left: robot components and sensor locations. Right: electrode placement for seven lower-limb muscles.')}</section>
<section class="section" id="video"><h2>Supplementary Video</h2><video class="project-video" controls playsinline preload="metadata" poster="../../assets/myomimetic-poster.jpg" aria-describedby="video-description"><source src="../../files/myomimetic-exosuit-video.mp4" type="video/mp4">Your browser does not support embedded video. <a href="../../files/myomimetic-exosuit-video.mp4">Download the video</a>.</video><p class="media-caption" id="video-description">1 min 49 sec · Device configuration, policy inputs, the training and deployment framework, and a deployed test session. The video includes on-screen explanatory text.</p></section>
<section class="section" id="results"><h2>Selected Findings</h2><p class="section-note">Selected results from the manuscript submitted to TNSRE.</p>

<article class="finding" id="measured-effort"><h3>Aggregate sEMG index versus motor-off</h3><p class="finding-summary">After signal-quality screening, the aggregate sEMG index across seven participants and three environments decreased by <strong>11.9% with BASE</strong> and <strong>15.7% with TGT</strong> relative to motor-off.</p><p class="result-context">Both policies reduced the aggregate sEMG index relative to motor-off. The BASE–TGT difference in this measure was not statistically significant. The index is derived from muscle activity; metabolic energy expenditure was not measured.</p>
<div class="figure-pair">{research_figure('layer2_effort_1col', 'Aggregate sEMG index for OFF, BASE, and TGT after signal-quality screening, pooled across terrains and separated by terrain.', 'Aggregate sEMG index. Pooled and terrain-specific comparisons of OFF, BASE, and TGT, with individual participant responses.')}
{research_figure('layer3_GM_1col', 'Measured and simulated gluteus maximus activation profiles and waveform overlap for OFF versus BASE and OFF versus TGT.', 'GM waveform comparison. Measured and simulated gluteus maximus activation and change-area overlap provide a muscle-specific view alongside the aggregate sEMG index.')}</div></article>
<article class="finding" id="response-direction"><h3>Simulated–measured response direction</h3><p class="finding-summary">Simulated and measured changes agreed in direction for <strong>12/21 muscle–terrain combinations with BASE</strong> and <strong>17/21 with TGT</strong>. Correlations between simulated and measured changes were −0.22 and 0.55, respectively.</p><p class="result-context">The between-policy difference in sign agreement was not statistically significant (p = .23).</p>
<div class="figure-pair">{research_figure('sim_effort_1col', 'Simulated gluteus maximus activation and normalized muscle effort for OFF, BASE, and TGT across level, incline, and stair ascent.', 'Simulation results. GM activation profiles and normalized muscle effort across the three terrains provide context for the simulated responses.')}
{research_figure('layer3_scatter_1col', 'Direction matrices and scatter plots comparing simulated and measured changes, with agreement of 12 out of 21 for BASE and 17 out of 21 for TGT.', 'Simulation versus measurement. Each point represents a muscle–terrain combination; the plots compare the direction and magnitude of change from motor-off.')}</div></article>
<article class="finding" id="bilateral-work"><h3>Critic comparison in simulation</h3><p class="finding-summary">Under the same BASE reward and a common 2 Hz force-command filter, the two critic configurations produced different force and work patterns. Positive work exceeded negative-work magnitude with the unified policy on all three terrains.</p><p class="result-context">Each configuration was trained once, and muscle-effort changes did not favor one configuration across all terrains; this comparison does not establish that one critic provides greater assistance.</p>
{research_figure('critic_ablation_1col', 'Unified versus independent critics: bilateral force profiles and positive and negative work across three terrains.', 'Critic ablation. Panel (a) compares right and left assistance-force profiles; panel (b) shows positive work above zero and negative work below zero. Solid and dashed force curves distinguish the two sides.', compact=True)}</article></section>
</main><footer class="footer"><a href="../../index.html">← Back to homepage</a><span>{h(profile['name'])} · {h(profile['updated'])}</span></footer></body></html>'''
    (dest/'index.html').write_text(page,encoding='utf-8')
