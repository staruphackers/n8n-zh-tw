#!/usr/bin/env python3
"""檢查原生繁中語言包；不載入 n8n、不連網、不寫入正式環境。"""
import argparse
from collections import Counter
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys

LOCALE_DIR = Path('packages/frontend/@n8n/i18n/src/locales')
KEEP_ENGLISH = {
    ('generic.enterprise',), ('generic.pro',), ('about.n8nLicense',),
    ('aiAssistant.name',),
}
PLACEHOLDER = re.compile(r"\{[^{}]*\}")
REFERENCE = re.compile(r"@(?:\.[A-Za-z]+)?:[A-Za-z0-9_.-]+")
CODE = re.compile(r'`[^`]+`|<code\b[^>]*>.*?</code>', re.S)
URL = re.compile(r'https?://[^\s<>\"\'`]+')
CJK = re.compile(r'[\u3400-\u9fff]')
TRANSLATABLE_ATTRIBUTES = {'title', 'alt', 'aria-label', 'placeholder'}


def reject_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'重複 JSON 鍵名：{key}')
        result[key] = value
    return result


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=reject_duplicates)


def leaves(obj, path=()):
    if isinstance(obj, dict):
        result = {}
        for key, value in obj.items():
            result.update(leaves(value, path + (key,)))
        return result
    if not isinstance(obj, str):
        raise ValueError(f'語言值必須為字串：{path!r}')
    return {path: obj}


def label(path):
    return '/' + '/'.join(part.replace('~', '~0').replace('/', '~1') for part in path)


class Markup(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.events = []

    def attributes(self, attrs):
        # 可翻譯 title 等顯示文字；不得改寫 href、target、class 或事件屬性。
        return tuple(sorted((key, None if key in TRANSLATABLE_ATTRIBUTES else value)
                            for key, value in attrs))

    def handle_starttag(self, tag, attrs):
        self.events.append(('start', tag, self.attributes(attrs)))

    def handle_startendtag(self, tag, attrs):
        self.events.append(('self', tag, self.attributes(attrs)))

    def handle_endtag(self, tag):
        self.events.append(('end', tag))

    def handle_entityref(self, name):
        self.events.append(('entity', name))

    def handle_charref(self, name):
        self.events.append(('charref', name))


def markup(text):
    parser = Markup()
    parser.feed(text)
    parser.close()
    return parser.events


def branches(text):
    # Vue i18n 的字面值 {'|'} 不得被誤判為複數分隔符號。
    masked = PLACEHOLDER.sub(lambda m: m.group().replace('|', '\x00'), text)
    return [part.replace('\x00', '|') for part in masked.split('|')]


def structural_errors(source, target):
    errors = []
    if source.strip() and not target.strip():
        errors.append('非空原文被翻成空白')
    source_branches, target_branches = branches(source), branches(target)
    if len(source_branches) != len(target_branches):
        errors.append('複數分支數不同')
    for index, (left, right) in enumerate(zip(source_branches, target_branches)):
        if Counter(PLACEHOLDER.findall(left)) != Counter(PLACEHOLDER.findall(right)):
            errors.append(f'第 {index + 1} 分支的插值或字面值不同')
    if Counter(REFERENCE.findall(source)) != Counter(REFERENCE.findall(target)):
        errors.append('共用字串參照不同')
    if Counter(CODE.findall(source)) != Counter(CODE.findall(target)):
        errors.append('程式碼片段不同')
    if Counter(URL.findall(source)) != Counter(URL.findall(target)):
        errors.append('網址不同')
    if markup(source) != markup(target):
        errors.append('HTML 標籤、非文字屬性或實體不同')
    return errors


def has_visible_english(text):
    text = CODE.sub('', text)
    text = REFERENCE.sub('', text)
    text = PLACEHOLDER.sub('', text)
    text = re.sub(r'<[^>]*>', '', text)
    text = URL.sub('', text)
    return bool(re.search(r'[A-Za-z]', text))


def inspect(source, target):
    original, translated = leaves(source), leaves(target)
    missing = sorted(set(original) - set(translated))
    extra = sorted(set(translated) - set(original))
    errors = []
    untranslated = []
    kept = []
    changed = []
    for key in sorted(set(original) & set(translated)):
        left, right = original[key], translated[key]
        errors.extend({'key': label(key), 'problem': problem}
                      for problem in structural_errors(left, right))
        if right == left and (key in KEEP_ENGLISH or not has_visible_english(left)):
            kept.append(key)
        elif right == left or (not CJK.search(right) and has_visible_english(right)):
            untranslated.append(key)
        else:
            changed.append(key)
    return {
        'scope': 'base-text-only; does not certify nodes, credentials, hardcoded UI or runtime loading',
        'source_leaf_count': len(original),
        'provided_leaf_count': len(translated),
        'changed_or_localized_count': len(changed),
        'retained_technical_or_reference_count': len(kept),
        'missing_count': len(missing),
        'untranslated_or_review_count': len(untranslated),
        'extra_count': len(extra),
        'structural_error_count': len(errors),
        'base_text_complete': not (missing or extra or errors or untranslated),
        'production_ready': False,
        'missing': [label(key) for key in missing],
        'untranslated_or_review': [label(key) for key in untranslated],
        'extra': [label(key) for key in extra],
        'structural_errors': errors,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument('--allow-partial', action='store_true', help='只檢查已翻譯項目的結構；不表示翻譯完成')
    parser.add_argument('--report', type=Path, help='另存完整 JSON 報告；只寫入指定檔案')
    args = parser.parse_args(argv)
    try:
        directory = args.root / LOCALE_DIR
        report = inspect(read_json(directory / 'en.json'), read_json(directory / 'zh-TW.json'))
        alias = directory / 'zh.json'
        if alias.exists() and read_json(alias) != read_json(directory / 'zh-TW.json'):
            raise ValueError('zh.json 相容語言檔必須與 zh-TW.json 完全一致')
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(json.dumps({k: v for k, v in report.items()
                          if k not in {'missing', 'untranslated_or_review', 'extra', 'structural_errors'}},
                         ensure_ascii=False, indent=2))
        for item in report['structural_errors'][:30]:
            print(f"ERROR {item['key']}: {item['problem']}", file=sys.stderr)
        for key in report['extra'][:30]:
            print(f'ERROR 未知鍵名：{key}', file=sys.stderr)
        if report['structural_error_count'] or report['extra_count']:
            return 1
        if not args.allow_partial and not report['base_text_complete']:
            print('尚未完成基礎字串翻譯。請勿以結構通過宣稱全介面完成。', file=sys.stderr)
            return 1
        return 0
    except (OSError, ValueError) as error:
        print(f'驗證失敗：{error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
