"""Build a reproducible, source-traceable China consumer-rights legal corpus.

The source documents are fetched from official Chinese government endpoints.
This script uses only Python's standard library plus requests.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import re
import time
import zipfile
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
import xml.etree.ElementTree as ET

import requests


ROOT = Path(__file__).resolve().parent
RAW = ROOT / "raw"
PROCESSED = ROOT / "processed"
NPC_BASE = "https://flk.npc.gov.cn"
NPC_DOWNLOAD = f"{NPC_BASE}/law-search/download/pc"
NPC_DETAILS = f"{NPC_BASE}/law-search/search/flfgDetails"
TODAY = date.today().isoformat()
STATUS_CHECKED_AT = "2026-10-09"
STATUS_LABELS = {1: "已废止", 2: "已修改", 3: "有效", 4: "尚未生效"}


SOURCES: list[dict[str, Any]] = [
    {
        "key": "consumer_protection_law",
        "title": "中华人民共和国消费者权益保护法",
        "kind": "法律",
        "publisher": "全国人民代表大会常务委员会",
        "published": "2013-10-25",
        "effective": "2014-03-15",
        "status": "有效",
        "status_code": 3,
        "status_source": "全国人大国家法律法规数据库，状态字段 sxx=3。",
        "status_checked_at": STATUS_CHECKED_AT,
        "version_note": "2013年修正文本；全国人大国家法律法规数据库标记为有效。",
        "bbbs": "2c909fdd678bf17901678bf7670606ef",
        "authority_url": f"{NPC_BASE}/",
        "verification_url": f"{NPC_DETAILS}?bbbs=2c909fdd678bf17901678bf7670606ef",
    },
    {
        "key": "consumer_protection_implementing_regulation",
        "title": "中华人民共和国消费者权益保护法实施条例",
        "kind": "行政法规",
        "publisher": "国务院",
        "published": "2024-03-15",
        "effective": "2024-07-01",
        "status": "有效",
        "status_code": 3,
        "status_source": "全国人大国家法律法规数据库，状态字段 sxx=3。",
        "status_checked_at": STATUS_CHECKED_AT,
        "version_note": "国务院令第778号；全国人大国家法律法规数据库标记为有效。",
        "bbbs": "ff808181927f09310192c2f4cd777281",
        "authority_url": "https://www.gov.cn/zhengce/content/202403/content_6940158.htm",
        "verification_url": f"{NPC_DETAILS}?bbbs=ff808181927f09310192c2f4cd777281",
    },
    {
        "key": "civil_code",
        "title": "中华人民共和国民法典",
        "kind": "法律",
        "publisher": "全国人民代表大会",
        "published": "2020-05-28",
        "effective": "2021-01-01",
        "status": "有效",
        "status_code": 3,
        "status_source": "全国人大国家法律法规数据库，状态字段 sxx=3。",
        "status_checked_at": STATUS_CHECKED_AT,
        "version_note": "全国人大国家法律法规数据库标记为有效；消费者合同相关规范需结合具体编、章检索。",
        "bbbs": "ff808081729d1efe01729d50b5c500bf",
        "authority_url": f"{NPC_BASE}/",
        "verification_url": f"{NPC_DETAILS}?bbbs=ff808081729d1efe01729d50b5c500bf",
    },
    {
        "key": "product_quality_law",
        "title": "中华人民共和国产品质量法",
        "kind": "法律",
        "publisher": "全国人民代表大会常务委员会",
        "published": "2018-12-29",
        "effective": "2018-12-29",
        "status": "有效",
        "status_code": 3,
        "status_source": "全国人大国家法律法规数据库，状态字段 sxx=3。",
        "status_checked_at": STATUS_CHECKED_AT,
        "version_note": "2018年修正文本；全国人大国家法律法规数据库标记为有效。",
        "bbbs": "ff8080816f135f46016f1d6dfd7614d3",
        "authority_url": f"{NPC_BASE}/",
        "verification_url": f"{NPC_DETAILS}?bbbs=ff8080816f135f46016f1d6dfd7614d3",
    },
    {
        "key": "advertising_law",
        "title": "中华人民共和国广告法",
        "kind": "法律",
        "publisher": "全国人民代表大会常务委员会",
        "published": "2021-04-29",
        "effective": "2021-04-29",
        "status": "有效",
        "status_code": 3,
        "status_source": "全国人大国家法律法规数据库，状态字段 sxx=3。",
        "status_checked_at": STATUS_CHECKED_AT,
        "version_note": "2021年修正文本；全国人大国家法律法规数据库标记为有效。",
        "bbbs": "ff8081817ab231eb017abd6bd860052d",
        "authority_url": f"{NPC_BASE}/",
        "verification_url": f"{NPC_DETAILS}?bbbs=ff8081817ab231eb017abd6bd860052d",
    },
    {
        "key": "food_safety_law",
        "title": "中华人民共和国食品安全法",
        "kind": "法律",
        "publisher": "全国人民代表大会常务委员会",
        "published": "2025-09-12",
        "effective": "2025-12-01",
        "status": "有效",
        "status_code": 3,
        "status_source": "全国人大国家法律法规数据库，状态字段 sxx=3。",
        "status_checked_at": STATUS_CHECKED_AT,
        "version_note": "2025年修正文本，已于2025-12-01施行；全国人大国家法律法规数据库标记为有效。",
        "bbbs": "7b5a76d0461745a08d3f964916b87ef3",
        "authority_url": f"{NPC_BASE}/",
        "verification_url": f"{NPC_DETAILS}?bbbs=7b5a76d0461745a08d3f964916b87ef3",
    },
    {
        "key": "ecommerce_law",
        "title": "中华人民共和国电子商务法",
        "kind": "法律",
        "publisher": "全国人民代表大会常务委员会",
        "published": "2018-08-31",
        "effective": "2019-01-01",
        "status": "有效",
        "status_code": 3,
        "status_source": "全国人大国家法律法规数据库，状态字段 sxx=3。",
        "status_checked_at": STATUS_CHECKED_AT,
        "version_note": "全国人大国家法律法规数据库标记为有效。",
        "bbbs": "2c909fdd678bf17901678bf8af050b81",
        "authority_url": f"{NPC_BASE}/",
        "verification_url": f"{NPC_DETAILS}?bbbs=2c909fdd678bf17901678bf8af050b81",
    },
    {
        "key": "prepaid_consumption_interpretation",
        "title": "最高人民法院关于审理预付式消费民事纠纷案件适用法律若干问题的解释",
        "kind": "司法解释",
        "publisher": "最高人民法院",
        "published": "2025-03-13",
        "effective": "2025-05-01",
        "status": "有效",
        "status_code": 3,
        "status_source": "全国人大国家法律法规数据库，状态字段 sxx=3。",
        "status_checked_at": STATUS_CHECKED_AT,
        "version_note": "法释〔2025〕4号；全国人大国家法律法规数据库标记为有效。",
        "bbbs": "ff808181927f0e7b0195d1a1c52d0287",
        "authority_url": "http://gongbao.court.gov.cn/Details/415add6e9c15736f2fbd871bdb1538.html",
        "verification_url": f"{NPC_DETAILS}?bbbs=ff808181927f0e7b0195d1a1c52d0287",
    },
    {
        "key": "food_drug_punitive_compensation_interpretation",
        "title": "最高人民法院关于审理食品药品惩罚性赔偿纠纷案件适用法律若干问题的解释",
        "kind": "司法解释",
        "publisher": "最高人民法院",
        "published": "2024-08-21",
        "effective": "2024-08-22",
        "status": "有效",
        "status_code": 3,
        "status_source": "全国人大国家法律法规数据库，状态字段 sxx=3。",
        "status_checked_at": STATUS_CHECKED_AT,
        "version_note": "法释〔2024〕9号；全国人大国家法律法规数据库标记为有效。",
        "bbbs": "ff80818192289516019240c1c890324a",
        "authority_url": f"{NPC_BASE}/",
        "verification_url": f"{NPC_DETAILS}?bbbs=ff80818192289516019240c1c890324a",
    },
]

# The SAMR page is the primary source. The State Council mirror provides a
# downloadable copy and includes the notice that this text was amended in 2020.
SUPPLEMENTAL_HTML = {
    "key": "online_seven_day_return_measure",
    "title": "网络购买商品七日无理由退货暂行办法",
    "kind": "部门规章",
    "publisher": "国家市场监督管理总局（原国家工商行政管理总局）",
    "published": "2017-01-06",
    "effective": "2017-03-15",
    "status": "官方修正文本；本条目未取得全国人大数据库状态码",
    "status_code": "",
    "status_source": "国务院官网镜像用于核实正文与2020年修正说明；未独立核验当前有效状态。",
    "status_checked_at": "未独立核验",
    "version_note": "国务院官方镜像文本注明：国家工商行政管理总局令第90号，2020-10-23依据市场监管总局令第31号修正。状态标记不等同于数据库现行性认定。",
    "authority_url": "https://www.samr.gov.cn/zw/zfxxgk/fdzdgknr/fgs/art/2023/art_26ca8fe29e184edd899fa0a7a060d935.html",
    "verification_url": "https://www.gov.cn/zhengce/zhengceku/2020-11/03/content_5557118.htm",
    "mirror_url": "https://www.gov.cn/zhengce/zhengceku/2020-11/03/content_5557118.htm",
}


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
ARTICLE_RE = re.compile(r"^(第[〇零一二三四五六七八九十百千万亿两\d]+条(?:之[〇零一二三四五六七八九十百千万亿两\d]+)?)\s*(.*)$")
HEADING_RE = re.compile(r"^(第[〇零一二三四五六七八九十百千万亿两\d]+[编章节])\s*(.*)$")
ARTICLE_NUMBER_RE = re.compile(r"^第([〇零一二三四五六七八九十百千万亿两\d]+)条(?:之([〇零一二三四五六七八九十百千万亿两\d]+))?$")


def clean_text(value: str) -> str:
    value = html.unescape(value).replace("\u00a0", " ").replace("\u3000", " ")
    value = value.replace("\r", " ").replace("\n", " ").replace("\t", " ")
    return re.sub(r"\s+", " ", value).strip()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def chinese_number(value: str) -> int:
    if value.isdigit():
        return int(value)
    digits = {"零": 0, "〇": 0, "一": 1, "二": 2, "两": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
    units = {"十": 10, "百": 100, "千": 1000}
    total = section = number = 0
    for char in value:
        if char in digits:
            number = digits[char]
        elif char in units:
            section += (number or 1) * units[char]
            number = 0
        elif char == "万":
            total += (section + number) * 10000
            section = number = 0
        elif char == "亿":
            total += (section + number) * 100000000
            section = number = 0
    return total + section + number


def validate_chunks(chunks: list[dict[str, str]]) -> dict[str, Any]:
    labels = [chunk["article_label"] for chunk in chunks]
    duplicate_labels = sorted({label for label in labels if labels.count(label) > 1})
    parsed: list[tuple[int, int]] = []
    for label in labels:
        match = ARTICLE_NUMBER_RE.match(label)
        if not match:
            raise RuntimeError(f"無法解析條號：{label}")
        base = chinese_number(match.group(1))
        suffix = chinese_number(match.group(2)) if match.group(2) else 0
        parsed.append((base, suffix))
    bases = sorted({base for base, _ in parsed})
    missing = [number for number in range(1, max(bases, default=0) + 1) if number not in bases]
    return {
        "empty_articles": sum(not chunk["text"].strip() for chunk in chunks),
        "duplicate_article_labels": duplicate_labels,
        "missing_article_numbers": missing,
        "ordered": parsed == sorted(parsed),
        "valid": not duplicate_labels and not missing and not any(not chunk["text"].strip() for chunk in chunks) and parsed == sorted(parsed),
    }


def fetch_npc_docx(session: requests.Session, source: dict[str, Any]) -> bytes:
    params = {"format": "docx", "bbbs": source["bbbs"], "fileId": ""}
    response = session.get(NPC_DOWNLOAD, params=params, timeout=45)
    response.raise_for_status()
    try:
        data = response.json().get("data", {})
    except ValueError as exc:
        raise RuntimeError(f"NPC 下载接口没有返回 JSON：{source['key']}") from exc
    signed_url = data.get("url")
    if not signed_url:
        raise RuntimeError(f"NPC 下载接口没有返回文件链接：{source['key']}")
    file_response = session.get(signed_url, timeout=90)
    file_response.raise_for_status()
    content = file_response.content
    if not content.startswith(b"PK\x03\x04"):
        raise RuntimeError(f"下载内容不是 DOCX：{source['key']} ({len(content)} bytes)")
    with zipfile.ZipFile(__import__("io").BytesIO(content)) as archive:
        if "word/document.xml" not in archive.namelist():
            raise RuntimeError(f"DOCX 缺少 word/document.xml：{source['key']}")
    return content


def docx_paragraphs(data: bytes) -> list[str]:
    with zipfile.ZipFile(__import__("io").BytesIO(data)) as archive:
        root = ET.fromstring(archive.read("word/document.xml"))
    paragraphs: list[str] = []
    for paragraph in root.findall(f".//{{{W_NS}}}body//{{{W_NS}}}p"):
        pieces: list[str] = []
        for node in paragraph.iter():
            if node.tag == f"{{{W_NS}}}t" and node.text:
                pieces.append(node.text)
            elif node.tag == f"{{{W_NS}}}tab":
                pieces.append(" ")
            elif node.tag in (f"{{{W_NS}}}br", f"{{{W_NS}}}cr"):
                pieces.append(" ")
        text = clean_text("".join(pieces))
        if text:
            paragraphs.append(text)
    return paragraphs


class OfficialPageParser(HTMLParser):
    """Extract paragraph text from the State Council UCAP-CONTENT block."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.content_depth = 0
        self.in_paragraph = False
        self.paragraph_depth = 0
        self.parts: list[str] = []
        self.paragraphs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        if tag == "div":
            if self.content_depth == 0 and attrs_dict.get("id") == "UCAP-CONTENT":
                self.content_depth = 1
            elif self.content_depth:
                self.content_depth += 1
        if self.content_depth and tag == "p":
            self.in_paragraph = True
            self.paragraph_depth += 1
            self.parts = []
        elif self.in_paragraph and tag == "br":
            self.parts.append(" ")

    def handle_endtag(self, tag: str) -> None:
        if self.in_paragraph and tag == "p":
            text = clean_text("".join(self.parts))
            if text:
                self.paragraphs.append(text)
            self.in_paragraph = False
            self.paragraph_depth = 0
            self.parts = []
        if tag == "div" and self.content_depth:
            self.content_depth -= 1

    def handle_data(self, data: str) -> None:
        if self.in_paragraph:
            self.parts.append(data)


def official_html_paragraphs(data: bytes) -> list[str]:
    parser = OfficialPageParser()
    parser.feed(data.decode("utf-8", "replace"))
    return parser.paragraphs


def article_chunks(paragraphs: list[str]) -> tuple[list[dict[str, str]], list[str]]:
    """Split source paragraphs into whole-article chunks without paraphrasing."""
    first_body_index = None
    for index, paragraph in enumerate(paragraphs):
        match = ARTICLE_RE.match(paragraph)
        if match and len(match.group(2).strip()) >= 5:
            first_body_index = index
            break
    if first_body_index is None:
        raise RuntimeError("无法识别正文中的首个带文本条文")

    active_heading = ""
    for paragraph in paragraphs[:first_body_index]:
        heading_match = HEADING_RE.match(paragraph)
        if heading_match:
            active_heading = clean_text(" ".join(heading_match.groups())).strip()

    chunks: list[dict[str, str]] = []
    preamble: list[str] = []
    for paragraph in paragraphs[:first_body_index]:
        if len(paragraph) > 20 and not ARTICLE_RE.match(paragraph) and not HEADING_RE.match(paragraph):
            # Keep enactment/amendment notes and exclude titles and TOC labels.
            if any(marker in paragraph for marker in ("修正", "施行", "公布", "通过", "命令", "法释", "主席令")):
                preamble.append(paragraph)

    current: dict[str, str] | None = None

    def flush() -> None:
        nonlocal current
        if current and current.get("text", "").strip():
            current["text"] = clean_text(current["text"])
            chunks.append(current)
        current = None

    for paragraph in paragraphs[first_body_index:]:
        heading_match = HEADING_RE.match(paragraph)
        if heading_match and not ARTICLE_RE.match(paragraph):
            active_heading = clean_text(" ".join(heading_match.groups())).strip()
            continue
        article_match = ARTICLE_RE.match(paragraph)
        if article_match:
            flush()
            label, remainder = article_match.groups()
            current = {"article_label": label.strip(), "chapter_title": active_heading, "text": remainder.strip()}
        elif current:
            current["text"] += " " + paragraph
    flush()
    if not chunks:
        raise RuntimeError("正文没有解析出条文")
    return chunks, preamble


def write_document(source: dict[str, Any], raw_data: bytes, paragraphs: list[str], raw_name: str) -> tuple[int, str, str]:
    chunks, preamble = article_chunks(paragraphs)
    validation = validate_chunks(chunks)
    if not validation["valid"]:
        raise RuntimeError(f"條文校驗失敗：{source['key']} {json.dumps(validation, ensure_ascii=False)}")
    raw_hash = sha256(raw_data)
    markdown_name = f"{source['key']}.md"
    markdown_path = PROCESSED / markdown_name
    metadata_rows = [
        f"# {source['title']}",
        "",
        f"- 类型：{source['kind']}",
        f"- 发布机关：{source['publisher']}",
        f"- 公布日期：{source.get('published') or '未核实'}",
        f"- 施行日期：{source.get('effective') or '未核实'}",
        f"- 状态：{source['status']}",
        f"- 状态来源：{source.get('status_source', '')}",
        f"- 状态核验日期：{source.get('status_checked_at', '未单独核验')}",
        f"- 版本说明：{source.get('version_note', '')}",
        f"- 官方来源：{source['authority_url']}",
        f"- 原始文件：../raw/{raw_name}",
        f"- SHA-256：{raw_hash}",
        "",
    ]
    if preamble:
        metadata_rows += ["## 公布与修正说明", "", *[f"> {line}" for line in preamble], ""]
    for chunk in chunks:
        metadata_rows.append(f"## {chunk['article_label']}")
        if chunk["chapter_title"]:
            metadata_rows.append(f"章节：{chunk['chapter_title']}")
        metadata_rows.extend(["", chunk["text"], ""])
    markdown_path.write_text("\n".join(metadata_rows), encoding="utf-8")

    with (PROCESSED / "articles.jsonl").open("a", encoding="utf-8", newline="") as output:
        for index, chunk in enumerate(chunks, start=1):
            record = {
                "chunk_id": f"{source['key']}:a{index:04d}",
                "document_id": source["key"],
                "document_title": source["title"],
                "document_type": source["kind"],
                "issuer": source["publisher"],
                "published_date": source.get("published"),
                "effective_date": source.get("effective"),
                "legal_status": source["status"],
                "legal_status_source": source.get("status_source", ""),
                "legal_status_checked_at": source.get("status_checked_at", ""),
                "version_note": source.get("version_note", ""),
                "chapter_title": chunk["chapter_title"],
                "article_label": chunk["article_label"],
                "text": chunk["text"],
                "source_url": source["authority_url"],
                "verification_url": source.get("verification_url", ""),
                "raw_file": f"raw/{raw_name}",
                "raw_sha256": raw_hash,
                "retrieved_at": TODAY,
            }
            output.write(json.dumps(record, ensure_ascii=False) + "\n")
    return len(chunks), markdown_name, raw_hash


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    article_jsonl = PROCESSED / "articles.jsonl"
    article_jsonl.write_text("", encoding="utf-8")
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (compatible; LegalCorpusBuilder/1.0)", "Referer": f"{NPC_BASE}/"})
    manifest: list[dict[str, Any]] = []
    quality: list[dict[str, Any]] = []

    for source in SOURCES:
        raw_name = f"npc_{source['key']}.docx"
        content = fetch_npc_docx(session, source)
        (RAW / raw_name).write_bytes(content)
        paragraphs = docx_paragraphs(content)
        count, md_name, digest = write_document(source, content, paragraphs, raw_name)
        manifest.append({
            **source,
            "database_id": source["bbbs"],
            "authority_url": source["authority_url"],
            "verification_url": source["verification_url"],
            "download_method": "全国人大国家法律法规数据库 download/pc API + 签名 DOCX 原件",
            "raw_file": f"raw/{raw_name}",
            "processed_file": f"processed/{md_name}",
            "raw_sha256": digest,
            "raw_bytes": len(content),
            "article_count": count,
            "checked_at": TODAY,
        })
        validation = validate_chunks(article_chunks(paragraphs)[0])
        quality.append({"document_id": source["key"], "paragraphs": len(paragraphs), "articles": count, **validation})
        time.sleep(0.2)

    supplemental = dict(SUPPLEMENTAL_HTML)
    response = session.get(supplemental["mirror_url"], timeout=45)
    response.raise_for_status()
    html_data = response.content
    html_name = f"gov_{supplemental['key']}.html"
    (RAW / html_name).write_bytes(html_data)
    html_paras = official_html_paragraphs(html_data)
    count, md_name, digest = write_document(supplemental, html_data, html_paras, html_name)
    manifest.append({
        **supplemental,
        "database_id": "",
        "download_method": "国务院官网官方镜像 HTML；另列市场监管总局官方文本页",
        "raw_file": f"raw/{html_name}",
        "processed_file": f"processed/{md_name}",
        "raw_sha256": digest,
        "raw_bytes": len(html_data),
        "article_count": count,
        "retrieved_at": TODAY,
    })
    validation = validate_chunks(article_chunks(html_paras)[0])
    quality.append({"document_id": supplemental["key"], "paragraphs": len(html_paras), "articles": count, **validation})

    fieldnames = list(dict.fromkeys(key for row in manifest for key in row))
    with (ROOT / "manifest.csv").open("w", encoding="utf-8-sig", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(manifest)

    (ROOT / "quality_report.json").write_text(
        json.dumps({"generated_at": TODAY, "documents": quality, "document_count": len(manifest), "article_count": sum(x["articles"] for x in quality)}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps({"document_count": len(manifest), "article_count": sum(x["articles"] for x in quality), "quality": quality}, ensure_ascii=True))


if __name__ == "__main__":
    main()
