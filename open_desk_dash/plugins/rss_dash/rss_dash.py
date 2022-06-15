import feedparser
from flask import Blueprint, render_template, request

api = Blueprint("rss_dash", __name__)


@api.route("/", methods=["GET"])
def rss_dash():
    link = request.args.get("link", default="", type=str)
    if not link:
        link = "https://www.nasa.gov/rss/dyn/lg_image_of_the_day.rss"
    rss_feed = feedparser.parse(link)
    rss_feed = find_images(rss_feed)
    return render_template(
        "rss_dash/rss_dash.html", feed=rss_feed.feed, items=rss_feed.entries[:10]
    )


def find_images(feeds: dict, limit=10) -> dict:
    """
    RSS Feed's appear to place image's in diff locations... so trying to find the fuckas
    """
    for entry in feeds.entries[:limit]:
        entry.image = find_image(entry)
    return feeds


def find_image(field) -> str:
    """Slow Recursion to find ANY(first) str that looks like an img link and use as the image"""
    if isinstance(field, dict):
        for val in field.values():
            img = find_image(val)
            if img:
                return img
    elif isinstance(field, list):
        for val in field:
            img = find_image(val)
            if img:
                return img
    elif (
        isinstance(field, str)
        and field.startswith("http")
        and (field.endswith("png") or field.endswith("jpg") or field.endswith("jpeg"))
    ):
        return field
