from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_home_hot_window_label_uses_24_hour_state() -> None:
    home_wxml = read_text("wechat-miniprogram/pages/home/home.wxml")
    home_js = read_text("wechat-miniprogram/pages/home/home.js")

    stale_label = "首页 2 " + "小时热帖"

    assert stale_label not in home_wxml
    assert "{{hotWindowTitle}}" in home_wxml
    assert 'const HOME_HOT_TITLE = "首页 24 小时热帖";' in home_js
    assert "/api/client/home/hot-topics" in home_js


def test_user_feed_does_not_render_owner_adoption_badge() -> None:
    web_js = read_text("app.js")
    web_css = read_text("styles.css")
    miniprogram_home_js = read_text("wechat-miniprogram/pages/home/home.js")
    miniprogram_home_wxss = read_text("wechat-miniprogram/pages/home/home.wxss")

    forbidden_labels = [
        "楼主" + "采纳评论",
        "楼主" + "已采纳",
        "博主" + "已采纳",
    ]
    for label in forbidden_labels:
        assert label not in web_js
        assert label not in miniprogram_home_js

    assert "post-badge " + "adopted" not in web_js
    assert ".post-badge." + "adopted" not in web_css
    assert ".post-badge." + "adopted" not in miniprogram_home_wxss
