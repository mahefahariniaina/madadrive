#!/usr/bin/env python3
"""Générateur du site MadaDrive.

Les pages sont écrites dans _pages/*.html (contenu seulement).
La première ligne de chaque page contient ses métadonnées :
<!--META {"path": "/tarifs/", "title": "...", "description": "...", "nav": "tarifs"} -->

Lancer :  python3 build.py
Le site complet est généré à la racine du dossier (prêt pour GitHub Pages).
"""
import json, re, pathlib, datetime, shutil, sys

ROOT = pathlib.Path(__file__).parent

# ─── À COMPLÉTER AVANT LA MISE EN LIGNE ─────────────────────────────
SITE = "https://madadrive.com"
WHATSAPP = "261329039795"
PHONE = "+261 32 90 397 95"
EMAIL = "contact@madadrive.com"    # TODO : créer l'adresse
HOURS = "7j/7, de 5 h à 22 h"      # TODO : confirmer les horaires
# ────────────────────────────────────────────────────────────────────

ICONS = {
    "chat": '<path d="M21 11.5a8.4 8.4 0 0 1-12.3 7.5L3 21l2-5.5A8.5 8.5 0 1 1 21 11.5z"/>',
    "phone": '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.9.6 2.8.7a2 2 0 0 1 1.7 2z"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    "pin": '<path d="M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 0 1 16 0z"/><circle cx="12" cy="10" r="3"/>',
    "car": '<path d="M19 17h2v-4l-2.5-5.5A2 2 0 0 0 16.7 6H7.3a2 2 0 0 0-1.8 1.5L3 13v4h2"/><circle cx="7.5" cy="17" r="2"/><circle cx="16.5" cy="17" r="2"/><path d="M9.5 17h5M3 13h18"/>',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="M9 12l2 2 4-4"/>',
    "user": '<circle cx="12" cy="8" r="4"/><path d="M4 21v-1a7 7 0 0 1 16 0v1"/>',
    "users": '<circle cx="9" cy="8" r="4"/><path d="M2 21v-1a7 7 0 0 1 14 0v1M16 3.1a4 4 0 0 1 0 7.8M22 21v-1a7 7 0 0 0-4-6.3"/>',
    "plane": '<path d="M17.8 19.2L16 11l3.5-3.5C21 6 21.5 4 21 3c-1-.5-3 0-4.5 1.5L13 8 4.8 6.2c-.5-.1-.9.1-1.1.5l-.3.5c-.2.5-.1 1 .3 1.3L9 12l-2 3H4l-1 1 3 2 2 3 1-1v-3l3-2 3.5 5.3c.3.4.8.5 1.3.3l.5-.2c.4-.3.6-.7.5-1.2z"/>',
    "map": '<path d="M9 3L3 6v15l6-3 6 3 6-3V3l-6 3-6-3z"/><path d="M9 3v15M15 6v15"/>',
    "heart": '<path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1-1.1a5.5 5.5 0 0 0-7.8 7.8l1 1L12 21l7.8-7.6 1-1a5.5 5.5 0 0 0 0-7.8z"/>',
    "fuel": '<path d="M3 22V5a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v17M2 22h14M15 10h2a2 2 0 0 1 2 2v4a1.5 1.5 0 0 0 3 0V8l-3-3M7 8h4"/>',
    "snow": '<path d="M12 2v20M2 12h20M5 5l14 14M19 5L5 19"/>',
    "star": '<path d="M12 2l3.1 6.3 6.9 1-5 4.9 1.2 6.8L12 17.8 5.8 21l1.2-6.8-5-4.9 6.9-1z"/>',
    "calendar": '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
    "wallet": '<path d="M20 12V8H6a2 2 0 0 1 0-4h12v4"/><path d="M4 6v12a2 2 0 0 0 2 2h14v-4"/><path d="M18 12a2 2 0 0 0 0 4h4v-4z"/>',
    "camera": '<path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/>',
    "menu": '<path d="M3 6h18M3 12h18M3 18h18"/>',
    "route": '<circle cx="6" cy="19" r="3"/><circle cx="18" cy="5" r="3"/><path d="M9 19h8.5a3.5 3.5 0 0 0 0-7h-11a3.5 3.5 0 0 1 0-7H15"/>',
}


def icon(name):
    return ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + ICONS[name] + '</svg>')


ROAD = ('<svg class="road" viewBox="0 0 1440 120" preserveAspectRatio="none" aria-hidden="true">'
        '<path d="M0 120 L0 92 Q720 -10 1440 70 L1440 120 Z" fill="#fff"/>'
        '<path d="M0 92 Q720 -10 1440 70" stroke="#FF9D2E" stroke-width="14" fill="none"/></svg>')

NAV = [
    ("location", "/location-voiture-madagascar/", "Location voiture"),
    ("minibus", "/location-minibus-avec-chauffeur/", "Minibus"),
    ("entreprises", "/location-voiture-entreprise/", "Entreprises"),
    ("aeroport", "/transfert-aeroport-ivato/", "Aéroport"),
    ("destinations", "/destinations/", "Destinations"),
    ("tarifs", "/tarifs/", "Tarifs"),
    ("blog", "/blog/", "Blog"),
    ("contact", "/contact/", "Contact"),
]


def quote_form(title="Votre devis en 2 minutes", sub="Réponse rapide sur WhatsApp, sans engagement."):
    return f'''<div class="quote">
<h2>{title}</h2>
<p class="small">{sub}</p>
<form class="js-quote" data-wa="{WHATSAPP}">
<div class="field"><label for="q-service">Prestation</label>
<select id="q-service" name="service">
<option>Journée avec chauffeur en ville (Tana)</option>
<option>Voyage en province</option>
<option>Transfert aéroport Ivato</option>
<option>Location au mois (entreprise)</option>
<option>Mariage</option>
<option>Événement</option>
<option>Autre demande</option>
</select></div>
<div class="field-row">
<div class="field"><label for="q-depart">Départ *</label><input id="q-depart" name="depart" required placeholder="Antananarivo"></div>
<div class="field"><label for="q-dest">Destination *</label><input id="q-dest" name="destination" required placeholder="Antsirabe…"></div>
</div>
<div class="field-row">
<div class="field"><label for="q-date">Dates ou période *</label><input id="q-date" name="periode" required placeholder="Ex. du 12 au 15 décembre"></div>
<div class="field"><label for="q-pax">Passagers *</label><select id="q-pax" name="passagers"><option>1 à 4</option><option>5 à 8</option><option>9 à 12 (maximum)</option></select></div>
</div>
<div class="field-row">
<div class="field"><label for="q-nom">Votre nom *</label><input id="q-nom" name="nom" required autocomplete="name"></div>
<div class="field"><label for="q-tel">Téléphone / WhatsApp *</label><input id="q-tel" type="tel" name="tel" required autocomplete="tel" placeholder="+261 34 …"></div>
</div>
<div class="field"><label for="q-mail">E-mail (facultatif)</label><input id="q-mail" type="email" name="email" autocomplete="email" placeholder="vous@exemple.com"></div>
<button class="btn btn-wa" type="submit">{icon("chat")} Recevoir mon devis sur WhatsApp</button>
<p class="note">Vous restez libre : aucun paiement en ligne.</p>
</form>
</div>'''


def cta(title="Prêt à prendre la route ?", text="Dites-nous où vous allez : nous vous répondons avec un prix clair, qui dit tout ce qui est inclus."):
    return f'''<section class="section"><div class="container"><div class="cta">
<h2>{title}</h2>
<p>{text}</p>
<div class="hero-ctas">
<a class="btn btn-wa" href="https://wa.me/{WHATSAPP}" target="_blank" rel="noopener">{icon("chat")} Écrire sur WhatsApp</a>
<a class="btn btn-ghost" href="tel:{PHONE.replace(' ', '')}">{icon("phone")} {PHONE}</a>
</div></div></div></section>'''


def header(active):
    links = "".join(
        f'<a href="{href}"{" aria-current=page" if key == active else ""}>{label}</a>' for key, href, label in NAV)
    return f'''<a class="skip" href="#main">Aller au contenu</a>
<header class="site-header"><div class="container header-inner">
<a class="brand" href="/" aria-label="MadaDrive, accueil"><img src="/assets/img/logo.png" alt="MadaDrive" width="640" height="112"></a>
<nav class="nav" id="nav" aria-label="Menu principal">{links}
<a class="btn btn-wa" href="https://wa.me/{WHATSAPP}" target="_blank" rel="noopener">{icon("chat")} WhatsApp</a></nav>
<button class="menu-toggle" aria-label="Ouvrir le menu" aria-expanded="false" aria-controls="nav">{icon("menu")}</button>
</div></header>'''


def footer():
    year = datetime.date.today().year
    return f'''<footer class="site-footer"><div class="container">
<div class="footer-grid">
<div class="footer-brand"><img src="/assets/img/logo-blanc.png" alt="MadaDrive" width="520" height="98" loading="lazy">
<p>Location de voiture avec chauffeur à Madagascar. Antananarivo et toutes les provinces.<br><b style="color:#fff">Madagascar, en toute confiance.</b></p></div>
<div><h3>Nos services</h3><ul>
<li><a href="/location-voiture-madagascar/">Location voiture Madagascar</a></li>
<li><a href="/location-minibus-avec-chauffeur/">Minibus 12 places avec chauffeur</a></li>
<li><a href="/transfert-aeroport-ivato/">Transfert aéroport Ivato</a></li>
<li><a href="/location-voiture-entreprise/">Location au mois entreprises</a></li>
<li><a href="/destinations/">Voyages en province</a></li></ul></div>
<div><h3>MadaDrive</h3><ul>
<li><a href="/tarifs/">Tarifs</a></li>
<li><a href="/blog/">Blog</a></li>
<li><a href="/a-propos/">À propos</a></li>
<li><a href="/contact/">Contact</a></li></ul></div>
<div><h3>Contact</h3><ul>
<li><a href="https://wa.me/{WHATSAPP}" target="_blank" rel="noopener">WhatsApp : {PHONE}</a></li>
<li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
<li>{HOURS}</li>
<li>Antananarivo, Madagascar</li></ul></div>
</div>
<div class="footer-bottom"><span>© {year} MadaDrive. Tous droits réservés.</span><span>Location de voiture avec chauffeur à Madagascar</span></div>
</div></footer>
<a class="wa-float" href="https://wa.me/{WHATSAPP}" target="_blank" rel="noopener" aria-label="Nous écrire sur WhatsApp">{icon("chat")}</a>'''


BUSINESS = {
    "@type": "AutoRental",
    "@id": SITE + "/#business",
    "name": "MadaDrive",
    "url": SITE + "/",
    "logo": SITE + "/assets/img/favicon-512.png",
    "image": SITE + "/assets/img/logo-slogan.png",
    "description": "Location de voiture et de minibus 12 places avec chauffeur à Antananarivo et dans toutes les provinces de Madagascar.",
    "slogan": "Madagascar, en toute confiance",
    "telephone": PHONE.replace(" ", ""),
    "email": EMAIL,
    "priceRange": "120 000 Ar / jour - 3 200 000 Ar / mois",
    "currenciesAccepted": "MGA, EUR",
    "address": {"@type": "PostalAddress", "addressLocality": "Antananarivo", "addressCountry": "MG"},
    "areaServed": {"@type": "Country", "name": "Madagascar"},
}


VERSION = datetime.datetime.now().strftime("%Y%m%d%H%M")


def page(meta, body):
    path = meta["path"]
    url = SITE + path
    graph = [BUSINESS, {"@type": "WebPage", "@id": url, "url": url, "name": meta["title"],
                        "description": meta["description"], "inLanguage": "fr",
                        "isPartOf": {"@type": "WebSite", "name": "MadaDrive", "url": SITE + "/"}}]
    if path != "/":
        crumbs = [("Accueil", "/")] + meta.get("crumbs", [(meta.get("crumb", meta["title"]), path)])
        graph.append({"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + p} for i, (n, p) in enumerate(crumbs)]})
    graph += meta.get("extra", [])
    # FAQ automatique : chaque <details> de la page devient une question de la FAQ
    faqs = re.findall(r"<details><summary>(.*?)</summary>\s*<p>(.*?)</p>", body, re.S)
    if faqs:
        graph.append({"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": re.sub("<[^>]+>", "", q),
             "acceptedAnswer": {"@type": "Answer", "text": re.sub("<[^>]+>", "", a)}} for q, a in faqs]})
    schema = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False)
    return f'''<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{meta["title"]}</title>
<meta name="description" content="{meta["description"]}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="MadaDrive">
<meta property="og:title" content="{meta["title"]}">
<meta property="og:description" content="{meta["description"]}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/assets/img/logo-slogan.png">
<meta property="og:locale" content="fr_FR">
<meta name="theme-color" content="#1261F3">
<link rel="icon" type="image/png" sizes="48x48" href="/assets/img/favicon-48.png">
<link rel="icon" type="image/png" sizes="512x512" href="/assets/img/favicon-512.png">
<link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Nunito:wght@800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/css/style.css?v={VERSION}">
<script type="application/ld+json">{schema}</script>
</head>
<body>
{header(meta.get("nav", ""))}
<main id="main">
{body}
</main>
{footer()}
<script src="/assets/js/main.js?v={VERSION}" defer></script>
</body>
</html>
'''


# Section « Nos chauffeurs » (accueil + à propos) : parcours de l'équipe, sans fiche nominative.
CHAUFFEURS = """<section class="section" id="chauffeurs"><div class="container">
<div class="head-row"><div><span class="label">Nos chauffeurs</span><h2>Des professionnels de la route, en ville comme en province</h2></div></div>
<p class="lead" style="margin:0 0 36px">Nos chauffeurs ne débutent pas. Ils ont passé des années au volant, dans les rues de Tana comme sur les routes nationales.</p>
<div class="grid g2">
<div class="card driver-path"><span class="big">15 ans de taxi</span><h3>Puis chauffeur personnel</h3><p>Des années de taxi dans les rues d'Antananarivo, puis chauffeur personnel, avec de nombreux longs trajets en région et sur les routes nationales. La ville, il la connaît rue par rue.</p></div>
<div class="card driver-path"><span class="big">7 ans et +</span><h3>Sur les routes nationales, en taxi-brousse</h3><p>Plus de 7 ans sur les grandes lignes nationales : ils connaissent les routes, les étapes, les passages difficiles et les bons arrêts.</p></div>
</div>
<div class="reasons" style="margin-top:48px">
<div class="reason"><span class="n">01</span><div><h3>Ils connaissent la route</h3><p>Embouteillages de Tana, routes régionales, RN2, RN4, RN7 : ils savent quand partir, par où passer et où s'arrêter.</p></div></div>
<div class="reason"><span class="n">02</span><div><h3>Ils vous comprennent</h3><p>Ils comprennent le français et l'anglais et parlent parfaitement malgache : aucune ambiguïté, que vous soyez touriste, de la diaspora ou d'ici.</p></div></div>
<div class="reason"><span class="n">03</span><div><h3>Zéro alcool, zéro tabac</h3><p>Nos chauffeurs ne boivent pas et ne fument pas. Vous voyagez dans un véhicule sain, avec quelqu'un de lucide au volant.</p></div></div>
<div class="reason"><span class="n">04</span><div><h3>Ouverts et accueillants</h3><p>Sociables, discrets et ponctuels : ils vous mettent à l'aise dès la prise en charge, en famille comme en rendez-vous d'affaires.</p></div></div>
</div>
</div></section>"""


def render(body):
    body = body.replace("{{QUOTE_FORM}}", quote_form())
    body = body.replace("{{ROAD}}", ROAD)
    body = body.replace("{{CTA}}", cta())
    body = body.replace("{{CHAUFFEURS}}", CHAUFFEURS)
    body = re.sub(r"\{\{ICON:(\w+)\}\}", lambda m: icon(m.group(1)), body)
    return (body.replace("{{WA}}", WHATSAPP).replace("{{PHONE}}", PHONE)
                .replace("{{PHONE_TEL}}", PHONE.replace(" ", "")).replace("{{EMAIL}}", EMAIL)
                .replace("{{HOURS}}", HOURS))


# ─── Blog ───────────────────────────────────────────────────────────
# Articles dans _blog/*.html, première ligne :
# <!--META {"slug": "...", "title": "titre SEO", "h1": "...", "description": "...",
#           "date": "2026-12-08", "category": "Guide", "excerpt": "..."} -->
# Un article n'est publié qu'à partir de sa date (publication programmée).
# Aperçu de tous les articles, même futurs :  python3 build.py --tout
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
        "septembre", "octobre", "novembre", "décembre"]


def date_fr(iso):
    d = datetime.date.fromisoformat(iso)
    return f"{d.day} {MOIS[d.month - 1]} {d.year}"


def reading_time(html):
    words = len(re.sub("<[^>]+>", " ", html).split())
    return max(1, round(words / 200))


def load_articles(include_future):
    today = datetime.date.today().isoformat()
    arts = []
    for src in sorted((ROOT / "_blog").glob("*.html")):
        raw = src.read_text(encoding="utf-8")
        m = re.match(r"<!--META (.*?) -->\n", raw, re.S)
        meta = json.loads(m.group(1))
        meta["content"] = raw[m.end():]
        meta["future"] = meta["date"] > today
        if include_future or not meta["future"]:
            arts.append(meta)
    return sorted(arts, key=lambda a: a["date"], reverse=True)


def article_page(a, others):
    path = f"/blog/{a['slug']}/"
    minutes = reading_time(a["content"])
    related = "".join(
        f'<li><a href="/blog/{o["slug"]}/">{o["h1"]}</a></li>' for o in others if o["slug"] != a["slug"])[:2000]
    body = f"""<section class="hero navy page-hero"><div class="container">
<div class="breadcrumb"><a href="/">Accueil</a> › <a href="/blog/">Blog</a> › {a['category']}</div>
<p class="kicker">{a['category']} · {date_fr(a['date'])} · {minutes} min de lecture</p>
<h1>{a['h1']}</h1>
<p class="lead">{a['excerpt']}</p>
</div>{{{{ROAD}}}}</section>

<section class="section"><div class="container article-grid">
<article class="prose article">
{a['content']}
</article>
<aside class="article-aside">
<div class="aside-box">
<h3>Besoin d'un chauffeur ?</h3>
<p>Minibus 12 places climatisé avec chauffeur, à Tana et en province.</p>
<p class="price" style="font-size:26px">120 000 Ar<small>la journée à Tana, carburant en plus</small></p>
<a class="btn btn-wa" style="width:100%" href="https://wa.me/{{{{WA}}}}" target="_blank" rel="noopener">{{{{ICON:chat}}}} Demander un devis</a>
<a class="aside-link" href="/tarifs/">Voir tous les tarifs →</a>
</div>
{('<div class="aside-box"><h3>À lire aussi</h3><ul class="aside-list">' + related + '</ul></div>') if related else ''}
</aside>
</div></section>
{{{{CTA}}}}"""
    meta = {"path": path, "title": a["title"], "description": a["description"], "nav": "blog",
            "crumbs": [("Blog", "/blog/"), (a["h1"], path)],
            "extra": [{"@type": "BlogPosting", "headline": a["h1"], "description": a["description"],
                       "datePublished": a["date"], "dateModified": a["date"], "inLanguage": "fr",
                       "mainEntityOfPage": SITE + path, "image": SITE + "/assets/img/logo-slogan.png",
                       "author": {"@type": "Organization", "name": "MadaDrive", "url": SITE + "/"},
                       "publisher": {"@id": SITE + "/#business"}}]}
    return path, page(meta, render(body))


def blog_index(arts):
    if arts:
        items = "".join(f"""<article class="post-row">
<p class="post-meta">{a['category']} · {date_fr(a['date'])}{' · <b>programmé</b>' if a['future'] else ''}</p>
<h2><a href="/blog/{a['slug']}/">{a['h1']}</a></h2>
<p>{a['excerpt']}</p>
<a class="post-more" href="/blog/{a['slug']}/">Lire l'article →</a>
</article>""" for a in arts)
    else:
        items = '<p class="lead">Les premiers articles arrivent bientôt : guides pratiques, budgets et récits de nos trajets.</p>'
    body = f"""<section class="hero navy page-hero"><div class="container">
<div class="breadcrumb"><a href="/">Accueil</a> › Blog</div>
<p class="kicker">Le carnet de route</p>
<h1>Voyager à Madagascar, conseils de chauffeurs</h1>
<p class="lead">Prix, itinéraires, temps de trajet, récits de nos voyages : tout ce qu'il faut savoir pour circuler sereinement à Madagascar.</p>
</div>{{{{ROAD}}}}</section>
<section class="section"><div class="container"><div class="post-list">
{items}
</div></div></section>
{{{{CTA}}}}"""
    meta = {"path": "/blog/", "title": "Blog : voyager à Madagascar avec chauffeur | MadaDrive",
            "description": "Prix de location, itinéraires, temps de trajet et récits de voyage : les conseils de MadaDrive pour circuler à Madagascar.",
            "nav": "blog", "crumb": "Blog"}
    return page(meta, render(body))


def build_blog(include_future):
    out_dir = ROOT / "blog"
    if out_dir.exists():
        shutil.rmtree(out_dir)
    arts = load_articles(include_future)
    urls = ["/blog/"]
    (out_dir).mkdir(parents=True)
    (out_dir / "index.html").write_text(blog_index(arts), encoding="utf-8")
    for a in arts:
        path, html = article_page(a, arts)
        f = ROOT / path.strip("/") / "index.html"
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(html, encoding="utf-8")
        if not a["future"]:
            urls.append(path)
        print("✓", path, "(programmé)" if a["future"] else "")
    return urls


def main():
    urls = []
    for src in sorted((ROOT / "_pages").glob("*.html")):
        raw = src.read_text(encoding="utf-8")
        m = re.match(r"<!--META (.*?) -->\n", raw, re.S)
        meta = json.loads(m.group(1))
        html = page(meta, render(raw[m.end():]))
        out = ROOT / meta["path"].strip("/") / "index.html" if meta["path"] != "/404/" else ROOT / "404.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html, encoding="utf-8")
        if meta["path"] != "/404/":
            urls.append(meta["path"])
        print("✓", meta["path"])
    urls += build_blog("--tout" in sys.argv)
    today = datetime.date.today().isoformat()
    sm = "".join(f"<url><loc>{SITE}{u}</loc><lastmod>{today}</lastmod></url>\n" for u in urls)
    (ROOT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{sm}</urlset>\n',
        encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
    (ROOT / "CNAME").write_text("madadrive.com\n", encoding="utf-8")
    print("✓ sitemap.xml, robots.txt, CNAME")


if __name__ == "__main__":
    main()
