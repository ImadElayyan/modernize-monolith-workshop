"""Build the focused, dependency-free student site: python site/build.py."""

from html import escape
from html.parser import HTMLParser
from pathlib import Path
import os
import shutil
import stat
from string import Template
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "site"
OUTPUT = ROOT / "_site"
PAGES = [
    ("index", "App Modernization with GitHub Copilot", "HOME"),
    ("overview", "Workshop overview", "START HERE"),
    ("setup", "Prepare your environment", "BEFORE THE WORKSHOP"),
    ("assess", "Assess and plan", "LAB 1 / MODULE 2B"),
    ("upgrade", "Upgrade and verify", "LAB 2 / MODULE 2B"),
    ("finish", "Review your results", "WRAP-UP"),
]
IMAGES = {
    "upgrade-menu.png": "2-upgrade-dotnet/2-upgrade-with-ghcp-modernization-app/images/upgrade-with-copilot.png",
    "upgrade-plan.png": "2-upgrade-dotnet/2-upgrade-with-ghcp-modernization-app/images/upgrade-plan.png",
    "blazor-example.png": "2-upgrade-dotnet/2-upgrade-with-ghcp-modernization-app/images/blazor-page-example.png",
}


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            if attrs["id"] in self.ids:
                raise ValueError(f"Duplicate ID: {attrs['id']}")
            self.ids.add(attrs["id"])
        for attr in ("href", "src"):
            if attr in attrs:
                self.links.append(attrs[attr])


def check_links():
    parsed = {}
    for path in OUTPUT.glob("*.html"):
        parser = Links()
        parser.feed(path.read_text(encoding="utf-8"))
        parsed[path.resolve()] = parser
    for page, parser in parsed.items():
        for link in parser.links:
            url = urlsplit(link)
            if url.scheme or url.netloc:
                continue
            target = (page.parent / unquote(url.path)).resolve() if url.path else page
            if not target.is_relative_to(OUTPUT.resolve()) or not target.is_file():
                raise ValueError(f"{page.name}: missing or invalid local link {link}")
            if url.fragment and target in parsed and unquote(url.fragment) not in parsed[target].ids:
                raise ValueError(f"{page.name}: missing anchor {link}")


def remove_readonly(function, path, error):
    # OneDrive can mark generated Windows directories read-only.
    if os.name != "nt" or not isinstance(error, PermissionError):
        raise error
    os.chmod(path, stat.S_IWRITE)
    function(path)


def build():
    # Delete only this script's generated output, never workshop source files.
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT, onexc=remove_readonly)
    (OUTPUT / "assets").mkdir(parents=True)
    for name in ("styles.css", "site.js"):
        shutil.copy2(SOURCE / name, OUTPUT / "assets" / name)
    for name, path in IMAGES.items():
        shutil.copy2(ROOT / path, OUTPUT / "assets" / name)
    shutil.copy2(ROOT / "LICENSE.md", OUTPUT / "LICENSE.txt")
    (OUTPUT / ".nojekyll").touch()
    template = Template((SOURCE / "template.html").read_text(encoding="utf-8"))
    for index, (slug, title, eyebrow) in enumerate(PAGES):
        nav = "\n".join(
            f'<a href="{key}.html"{" aria-current=\"page\"" if key == slug else ""}>'
            f'<span class="nav-number">{number:02}</span>{escape(label)}</a>'
            for number, (key, label, _) in enumerate(PAGES[1:])
        )
        previous = (
            f'<a class="button secondary" href="{PAGES[index - 1][0]}.html">'
            f'Previous: {escape(PAGES[index - 1][1])}</a>' if index else ""
        )
        following = (
            f'<a class="button" href="{PAGES[index + 1][0]}.html">'
            f'Next: {escape(PAGES[index + 1][1])}</a>' if index + 1 < len(PAGES) else
            '<a class="button" href="index.html">Back to overview</a>'
        )
        result = template.substitute(
            title=escape(title), eyebrow=escape(eyebrow), nav=nav,
            content=(SOURCE / "content" / f"{slug}.html").read_text(encoding="utf-8"),
            previous=previous, following=following,
            body_class="site-home" if slug == "index" else "site-step",
            heading="" if slug == "index" else (
                f'<p class="eyebrow">{escape(eyebrow)}</p><h1>{escape(title)}</h1>'
            ),
            header_nav=(
                (f'<a class="nav-button" href="{PAGES[index - 1][0]}.html">Prev</a>' if index else "")
                + (f'<a class="nav-button" href="{PAGES[index + 1][0]}.html">Next</a>' if index + 1 < len(PAGES) else "")
            ),
        )
        (OUTPUT / f"{slug}.html").write_text(result, encoding="utf-8")
    check_links()
    print(f"Built {len(PAGES)} pages; all local links and anchors resolve: {OUTPUT}")


if __name__ == "__main__":
    build()
