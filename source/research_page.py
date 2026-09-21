"""Static project page for the supplied manuscript and supplementary video."""
from html import escape as h
from hashlib import sha256

def stylesheet_href(site, prefix):
    # A new URL when styles change prevents stale CSS after a Pages deployment.
    version = sha256((site/'assets/style.css').read_bytes()).hexdigest()[:12]
    return f'{prefix}assets/style.css?v={version}'

RESEARCH_FIGURES = {
    'system': (2000, 778),
    'networks': (2000, 908),
    'setup': (2000, 990),
    'critic_ablation_1col': (2000, 1905),
    'layer2_effort_1col': (2000, 1461),
    'layer3_GM_1col': (1537, 2000),
    'sim_effort_1col': (1727, 2000),
    'layer3_scatter_1col': (2000, 1500),
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

def build_research_index(site, profile):
    dest = site/'research'
    dest.mkdir(parents=True, exist_ok=True)
    studies = ''
    for m in profile.get('manuscripts', []):
        authors = h(m['authors']).replace(h(profile['name']),'<strong>'+h(profile['name'])+'</strong>')
        details = '../'+m['url']
        video = f'<video id="myomimetic-video" class="project-video" controls playsinline preload="metadata" poster="../{h(m["thumbnail"])}" aria-label="Research video: {h(m["title"])}"><source src="../{h(m["video_url"])}" type="video/mp4">Your browser does not support embedded video.</video>' if m.get('video_url') else ''
        studies += f'''<article class="research-study"><p class="eyebrow">ONGOING RESEARCH</p><h2><a href="{h(details)}">{h(m['title'])}</a></h2><p class="authors">{authors}</p><p class="section-note">{h(m.get('relation',''))} {h(m['status'])}.</p><p class="study-summary">{h(m.get('description',''))}</p>{video}<p class="study-more"><a href="{h(details)}">Study details <span aria-hidden="true">→</span></a></p></article>'''
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
    thesis_note = f'<p class="section-note">This journal manuscript extends Dongmin Go\'s master\'s thesis, <em>{h(manuscript["thesis_title"])}</em> (Chung-Ang University, 2025). Work in progress; not yet submitted.</p>' if manuscript.get('thesis_title') else ''
    page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Myomimetic Exosuit Assistance | {h(profile['name'])}</title>
<meta name="description" content="A unified-critic multi-agent reinforcement learning framework connecting musculoskeletal simulation, embedded control, and hardware evaluation across three walking environments.">
<link rel="stylesheet" href="{stylesheet_href(site, '../../')}"><link rel="icon" href="../../assets/favicon.svg" type="image/svg+xml">
<link rel="canonical" href="{h(profile['website'])}research/myomimetic-exosuit/">
</head><body class="project-page"><a class="skip" href="#main">Skip to content</a>
{site_navigation('research','../../index.html','../index.html')}
<main class="project-main" id="main"><header class="project-header"><p class="eyebrow">MANUSCRIPT IN PREPARATION</p><h1>{h(manuscript['title'])}</h1><p class="project-authors">{authors}</p><p class="project-affiliations">Chung-Ang University · HUROTICS</p></header>
<section class="section" id="overview"><h2>Overview</h2>{thesis_note}<p>This study investigates how a shared critic shapes coordination between a simulated musculoskeletal model and a bilateral hip-extension exosuit. Both policies learn in a coupled physical environment, while only the exosuit policy is deployed on the real device.</p><p>The framework covers level walking, incline walking, and stair ascent without reference-motion tracking. On hardware, the controller uses IMU and past-action histories, without requiring terrain labels or muscle-state measurements.</p>
{research_figure('system', 'System overview linking coupled musculoskeletal simulation to exosuit deployment across level walking, incline walking, and stair ascent.', 'System overview. Muscle and exosuit policies learn together in simulation; the exosuit policy is then deployed and evaluated across three terrains.')}
<p class="figure-hint">Select any figure to view it at full resolution.</p>
<div class="method-grid"><article><h3>Joint learning</h3><p>Centralized training with a unified critic and decentralized execution. A matched-actor, matched-reward comparison evaluates an independent-critic alternative.</p></article><article><h3>Embedded control</h3><p>Policy inference at 50 Hz on a Jetson Orin Nano. Force commands travel over CAN to the robot's 1 kHz low-level controller.</p></article><article><h3>Hardware evaluation</h3><p>Two reward variants, BASE and TGT, are compared with motor-off assistance in seven healthy participants across three environments.</p></article></div></section>
<section class="section" id="architecture"><h2>Network Architecture</h2><p>The muscle and exosuit policies share a unified critic during training. The exosuit policy combines long and short histories of IMU observations and past actions, and the same policy is shared between the left and right sides.</p>
{research_figure('networks', 'Muscle policy, unified critic, and shared bilateral exosuit policy with a dual-history encoder and hardware deployment pathway.', 'Network architecture. The exosuit policy uses 2 s and 80 ms histories; only this policy is transferred to hardware, followed by filtering and force scaling.')}</section>
<section class="section" id="experimental-setup"><h2>Experimental Setup</h2><p>The wearable system combines an onboard inference computer, inertial sensors, and force sensing. EMG electrodes record activity from seven lower-limb muscles during the hardware evaluation.</p>
{research_figure('setup', 'Exosuit hardware configuration and EMG electrode placement for GM, RF, VL, BF, TA, MG, and SOL.', 'Experimental setup. Left: robot components and sensor locations. Right: EMG electrode placement; the GM electrode is hidden by clothing.')}</section>
<section class="section" id="video"><h2>Supplementary Video</h2><video class="project-video" controls playsinline preload="metadata" poster="../../assets/myomimetic-poster.jpg" aria-describedby="video-description"><source src="../../files/myomimetic-exosuit-video.mp4" type="video/mp4">Your browser does not support embedded video. <a href="../../files/myomimetic-exosuit-video.mp4">Download the video</a>.</video><p class="media-caption" id="video-description">1 min 49 sec · Device configuration, policy inputs, the training and deployment framework, and a deployed test session. The video includes on-screen explanatory text.</p></section>
<section class="section" id="results"><h2>Selected Findings</h2><p class="section-note">Results reported in the current draft.</p>
<article class="finding" id="bilateral-work"><h3>Bilateral positive-work difference in simulation</h3><p class="finding-summary">Bilateral positive-work differences were <strong>4–14% with a unified critic</strong>, compared with <strong>22–49% with independent critics</strong>.</p>
{research_figure('critic_ablation_1col', 'Unified versus independent critics: bilateral exosuit force profiles and positive-work differences across three terrains.', 'Critic ablation. Panel (a) compares right and left assistance-force profiles; panel (b) compares positive work. Solid and dashed lines distinguish the two sides.', compact=True)}</article>
<article class="finding" id="measured-effort"><h3>EMG-derived aggregate effort versus motor-off</h3><p class="finding-summary">Across seven participants and three environments, aggregate effort decreased by <strong>15.5% with BASE</strong> and <strong>19.1% with TGT</strong> relative to motor-off.</p><p class="result-context">Both policies reduced aggregate effort relative to motor-off. The BASE–TGT difference in this measure was not statistically significant. These are EMG-derived muscle-effort results, not measurements of metabolic energy expenditure.</p>
<div class="figure-pair">{research_figure('layer2_effort_1col', 'Measured normalized muscle effort for OFF, BASE, and TGT, pooled across terrains and separated by terrain, with seven participant traces.', 'Aggregate effort. Pooled and terrain-specific comparisons of OFF, BASE, and TGT, with individual participant responses.')}
{research_figure('layer3_GM_1col', 'Measured and simulated gluteus maximus activation profiles and waveform overlap for OFF versus BASE and OFF versus TGT.', 'GM waveform comparison. Measured and simulated gluteus maximus activation and waveform overlap provide a muscle-specific view alongside the aggregate effort result.')}</div></article>
<article class="finding" id="response-direction"><h3>Simulated–measured response direction</h3><p class="finding-summary">Simulated and measured changes agreed in direction for <strong>11/21 muscle–terrain combinations with BASE</strong> and <strong>17/21 with TGT</strong>.</p>
<div class="figure-pair">{research_figure('sim_effort_1col', 'Simulated gluteus maximus activation and normalized muscle effort for OFF, BASE, and TGT across level, incline, and stair ascent.', 'Simulation results. GM activation profiles and normalized muscle effort across the three terrains provide context for the simulated responses.')}
{research_figure('layer3_scatter_1col', 'Scatter plots comparing simulated and measured percentage changes, with same-sign agreement of 11 out of 21 for BASE and 17 out of 21 for TGT.', 'Simulation versus measurement. Each point represents a muscle–terrain combination; the plots compare the direction and magnitude of change from motor-off.')}</div></article></section>
</main><footer class="footer"><a href="../../index.html">← Back to homepage</a><span>{h(profile['name'])} · {h(profile['updated'])}</span></footer></body></html>'''
    (dest/'index.html').write_text(page,encoding='utf-8')
