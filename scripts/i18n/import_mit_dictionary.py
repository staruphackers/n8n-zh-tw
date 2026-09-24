#!/usr/bin/env python3
"""匯入固定 MIT 快照的純文字字典；不執行第三方安裝器，不修改 n8n 功能。"""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.request import Request, urlopen

from validate_zh_tw import CJK, has_visible_english, inspect, leaves, read_json, read_source, structural_errors

SOURCE_REPO = 'Melaszzzz/n8n-localization'
SOURCE_COMMIT = '3b4b5f2e19159009f364d057e24f4b61769c5e43'
SOURCE_PARTS = {
    'admin_projects_extra.json': '8c33ff7e74c5d72fbe50cd4e03131774d8fd8afb',
    'ai_chat_extra.json': 'ab7144d9c621a17093bbefd8e9e51bb42a58171d',
    'catchall_common_extra.json': '3e918f7d04c042cac1796f5e498648ccf1fa73bc',
    'common_accessibility_extra.json': '82ade9f16c630bef6f2bc87e503b84d31a1f72b4',
    'community_nodes_ui.json': '0967ef424bce6791893e9a57bb952f80fd536e93',
    'core.json': '0cb54613e06757e595bebbe8c9352f0610e370b4',
    'editor.json': '5ffc7d5da1f139c2124dc81a2f4e6e018408e6e0',
    'editor_extra.json': '8b4d5c26cfd03b22506f2b5736bb2bb8329cbf1b',
    'evaluations_insights_extra.json': '8abd0dfcdd1f87976b56f72c4e41ebe51702ea56',
    'forms_webhook_extra.json': 'dcba2cff352c471d673d4b7f178461d065d4c48a',
    'home_credentials_extra.json': '22c5712c906734680e3cba1e90194964fae440f8',
    'navigation.json': '4553c0262ffaf83ff9b26b9ec2d064e4720e4999',
    'node_2_34_4.json': 'a28e05cad5ddf8eccd963ccc34e6783756652149',
    'node_ai_core.json': '6e29d2baf760b602aa02ea3707a24d18b4cf31e0',
    'node_config_technical_extra.json': '57176defa97434d77ddcf22c7d627ccd8deabea6',
    'node_core_processing.json': '761e22c6425d2da67964860109c1c44731c54494',
    'node_full_coverage.json': 'e4f40f6288ef42ff59f1c0256418d01a7fb29c64',
    'node_google_workspace.json': 'fd55e74cd8db395031236836a3df171f8336f0f1',
    'node_runtime_ui_extra.json': 'd0c34299f77dc0d6029073c8de98313e1e4ec89f',
    'node_schedule.json': 'f28d65e2ba230580cd6300538d5c9a8685edc3c2',
    'node_tool_workflow.json': '6e69a4259044fd1be6b5b93792a9cea367900fad',
    'node_triggers_core.json': '067de3a083210963bf4b85279f94b0fd99e06165',
    'parity_ai_platform.json': '0a6b7ea32701e2691cf4b2934a23abdc832cfa07',
    'parity_catchall.json': '4d92796b2380a6b41ee6907112b40bdcf955ea05',
    'parity_editor.json': '25eec379e9c6afc05f0997192447137e928659a1',
    'parity_editor_longtail.json': '1ee9c6eaaf244657cc75c0efb64cb02826fdd12f',
    'parity_settings.json': '1460449d358b912b10becfd658c17a95fcf6a89e',
    'settings.json': 'c87bc4ebeca32dcd7bffce46f9680c794dafb6cd',
    'settings_extra.json': 'ef7f87314202c2f87f813a43fccc4d3288556ade',
    'trigger_panel_extra.json': 'e5aa9e437c64800c33c1f1626f5362c37fb2f0e1',
}
LEGAL = {
    'LICENSE': '3df14a11de3460e79a171ac2494dea7572f9fab5',
    'NOTICE': '5cfbb50bbaf627861d09be0d28e0fbaf2659e491',
    'localization/PROVENANCE.md': '09a891f96b75dfb18cfb4d7108053b36d768dd67',
}
PROTECTED = re.compile(r'```[\s\S]*?```|`[^`]+`|<code\b[^>]*>[\s\S]*?</code>|\{[^{}]*\}|@(?:\.[A-Za-z]+)?:[\w.-]+|https?://[^\s<>"\'`]+|<[^>]+>')
DISPLAY_ATTRIBUTE = re.compile(r'\b(title|alt|aria-label|placeholder)=("([^"]*)"|\'([^\']*)\')')
TERMS = [
    ('工作流', '工作流程'), ('憑據', '憑證'), ('默認', '預設'), ('保存', '儲存'),
    ('設置', '設定'), ('配置', '設定'), ('添加', '新增'), ('創建', '建立'),
    ('數據', '資料'), ('加載', '載入'), ('導入', '匯入'), ('導出', '匯出'),
    ('用戶', '使用者'), ('客戶端', '用戶端'), ('服務器', '伺服器'), ('支持', '支援'), ('網絡', '網路'),
    ('信息', '資訊'), ('鏈接', '連結'), ('運行', '執行'), ('調試', '偵錯'),
    ('腳本', '指令碼'), ('禁用', '停用'), ('字符串', '字串'), ('數組', '陣列'),
    ('布爾', '布林'), ('程序', '程式'), ('函數', '函式'), ('字段', '欄位'),
    ('列表', '清單'), ('正則表達式', '正規表示式'), ('表達式', '運算式'),
    ('佈局', '版面配置'), ('模板', '範本'), ('主頁', '首頁'), ('剪貼板', '剪貼簿'),
    ('緩存', '快取'), ('實例', '執行個體'), ('質量', '品質'), ('視頻', '影片'),
    ('音頻', '音訊'), ('硬件', '硬體'), ('軟件', '軟體'), ('登錄', '登入'),
    ('賬戶', '帳號'), ('文檔', '文件'), ('描述', '說明'), ('反饋', '回饋'), ('訪問', '存取'), ('執行記錄', '執行紀錄'),
]


def blob_sha(data):
    return hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()


def download(path, expected_sha, cache):
    target = cache / expected_sha
    if target.exists():
        data = target.read_bytes()
    else:
        url = f'https://raw.githubusercontent.com/{SOURCE_REPO}/{SOURCE_COMMIT}/{path}'
        with urlopen(Request(url, headers={'User-Agent': 'n8n-zh-tw-localization-audit'}), timeout=40) as response:
            data = response.read(5_000_001)
        if len(data) > 5_000_000:
            raise ValueError('來源檔超過允許大小')
    if blob_sha(data) != expected_sha:
        raise ValueError(f'來源雜湊不符：{path}')
    cache.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return data


def convert_text(text, original, converter):
    def prose(value):
        value = converter.convert(value)
        for before, after in TERMS:
            if before == '工作流':
                value = re.sub(r'工作流(?!程)', after, value)
            else:
                value = value.replace(before, after)
        if re.search(r'\bprojects?\b', original, re.I):
            value = value.replace('項目', '專案')
        if re.search(r'\bobjects?\b', original, re.I):
            value = value.replace('對象', '物件')
        if re.search(r'\bfiles?\b', original, re.I) and not re.search(r'\bdocs?|documentation|documents?\b', original, re.I):
            value = value.replace('文件', '檔案')
        value = re.sub(r'本地(?!化)', '本機', value)
        if re.search(r'\b(?:AI|LLM|model|tokens|token usage)\b', original, re.I):
            value = value.replace('令牌', 'token')
        else:
            value = value.replace('令牌', '權杖')
        return value

    result = []
    position = 0
    for match in PROTECTED.finditer(text):
        result.append(prose(text[position:match.start()]))
        protected = match.group()
        if protected.startswith('<') and not protected.startswith('<code'):
            def convert_attribute(attribute):
                quote = attribute.group(2)[0]
                content = attribute.group(3) if attribute.group(3) is not None else attribute.group(4)
                return f'{attribute.group(1)}={quote}{prose(content)}{quote}'
            protected = DISPLAY_ATTRIBUTE.sub(convert_attribute, protected)
        result.append(protected)
        position = match.end()
    result.append(prose(text[position:]))
    return ''.join(result)


def set_path(target, key, value):
    obj = target
    for part in key[:-1]:
        obj = obj.setdefault(part, {})
    obj[key[-1]] = value


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent='\t') + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument('--output', type=Path, required=True, help='產物暫存目錄；不直接改寫 Repo')
    parser.add_argument('--cache', type=Path, required=True)
    args = parser.parse_args()
    from opencc import OpenCC
    converter = OpenCC('s2twp')
    out = args.output
    legal_bytes = {path: download(path, sha, args.cache) for path, sha in LEGAL.items()}
    if not legal_bytes['LICENSE'].startswith(b'MIT License\n'):
        raise ValueError('固定快照的授權不是預期的 MIT')
    raw_memory = defaultdict(set)
    for name, sha in SOURCE_PARTS.items():
        data = json.loads(download(f'localization/parts/{name}', sha, args.cache))
        for original, translation in data.items():
            if not isinstance(original, str) or not isinstance(translation, str):
                raise ValueError(f'非文字字典資料：{name}')
            raw_memory[original].add(translation)
    explicit = json.loads(download('localization/overrides.json', '449fd2e42b74cc2bba9a417252ecaae00af2b480', args.cache))
    for original, translation in explicit.items():
        raw_memory[original] = {translation}
    memory = {}
    conflicts = {}
    rejected = {}
    for original, translations in raw_memory.items():
        converted = {convert_text(value, original, converter) for value in translations}
        if len(converted) != 1:
            conflicts[original] = sorted(converted)
            continue
        candidate = next(iter(converted))
        problems = structural_errors(original, candidate)
        if problems:
            rejected[original] = {'candidate': candidate, 'problems': problems}
            continue
        if CJK.search(candidate) or not has_visible_english(original):
            memory[original] = candidate
        elif original == candidate:
            memory[original] = candidate
        else:
            rejected[original] = {'candidate': candidate, 'problems': ['沒有中文且不同於原文，需人工確認']}
    locale_path = Path('packages/frontend/@n8n/i18n/src/locales/zh-TW.json')
    overrides_path = Path('localization/zh-TW/overrides.json')
    if (args.root / overrides_path).exists():
        overrides = read_json(args.root / overrides_path)
    else:
        initial = (args.root / locale_path).read_bytes()
        if blob_sha(initial) != 'd2153c196778bedfdf718d4869a5cf2b7eba3239':
            raise ValueError('缺少人工覆寫來源，且目前語言檔不是已確認的起始版本')
        overrides = json.loads(initial)
    # 後續補譯可拆成檔案，合併時不允許跨檔案重複鍵。
    override_leaves = leaves(overrides)
    for path in sorted((args.root / 'localization/zh-TW/patches').glob('*.json')):
        for key, value in leaves(read_json(path)).items():
            if key in override_leaves:
                raise ValueError(f'人工補譯鍵重複：{path.name}: {key}')
            override_leaves[key] = value
    source, source_duplicates = read_source(args.root / 'packages/frontend/@n8n/i18n/src/locales/en.json')
    source_leaves = leaves(source)
    unknown = set(override_leaves) - set(source_leaves)
    if unknown:
        raise ValueError(f'人工覆寫包含未知鍵：{sorted(unknown)[:5]}')
    target = {}
    missing = []
    technical_review = []
    for key, original in source_leaves.items():
        candidate = override_leaves.get(key, memory.get(original))
        if candidate is None and not has_visible_english(original):
            candidate = original
        if candidate is None:
            missing.append({'key': list(key), 'source': original, 'conflict': conflicts.get(original), 'rejected': rejected.get(original)})
            continue
        problems = structural_errors(original, candidate)
        if problems:
            raise ValueError(f'人工或合併譯文結構不符：{key}: {problems}')
        set_path(target, key, candidate)
        if candidate == original and has_visible_english(original):
            technical_review.append({'key': list(key), 'source': original})
    report = inspect(source, target)
    report['source_duplicate_keys'] = source_duplicates
    report['dictionary_source'] = {'repository': SOURCE_REPO, 'commit': SOURCE_COMMIT, 'tag': 'v0.3.0', 'license': 'MIT', 'baseline': '2.34.4'}
    report['conversion'] = 'OpenCC 0.1.7 s2twp + Taiwan glossary + manual overrides; not a human review certificate'
    report['memory_entry_count'] = len(memory)
    report['memory_conflict_count'] = len(conflicts)
    report['memory_rejected_count'] = len(rejected)
    write_json(out / locale_path, target)
    write_json(out / overrides_path, overrides)
    write_json(out / 'localization/zh-TW/phrase-memory.json', dict(sorted(memory.items())))
    write_json(out / 'localization/zh-TW/missing-base.json', missing)
    write_json(out / 'localization/zh-TW/technical-review.json', technical_review)
    write_json(out / 'localization/zh-TW/coverage.json', report)
    for path, data in legal_bytes.items():
        name = Path(path).name
        target_path = out / 'localization/vendor/melas-v0.3.0' / name
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_bytes(data)
    print(json.dumps({key: value for key, value in report.items() if key not in {'missing', 'extra', 'untranslated_or_review', 'structural_errors'}}, ensure_ascii=False, indent=2))
    print('FIRST_MISSING', json.dumps(missing[:8], ensure_ascii=False))
    print('產物只寫入指定暫存目錄；尚未更新分支或部署。')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError) as error:
        print(f'匯入失敗：{error}', file=sys.stderr)
        raise SystemExit(1)
