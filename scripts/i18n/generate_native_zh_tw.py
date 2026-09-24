#!/usr/bin/env python3
"""只讀取同版本 npm 套件的 JSON 描述；不安裝、不執行套件或連接正式主機。"""
import argparse
import base64
from collections import defaultdict
import hashlib
import io
import json
from pathlib import Path
import re
import tarfile
from urllib.error import HTTPError
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen

from retained_zh_tw import retained_reason
from validate_zh_tw import CJK, leaves, read_json, read_source, structural_errors

PACKAGES = {
    'n8n-nodes-base': 'packages/nodes-base/package.json',
    '@n8n/n8n-nodes-langchain': 'packages/@n8n/nodes-langchain/package.json',
}
BAD_KEYS = {'__proto__', 'prototype', 'constructor'}
TEXT_FIELDS = ('displayName', 'description', 'placeholder', 'hint')


def get(url, limit):
    if urlparse(url).scheme != 'https' or urlparse(url).hostname != 'registry.npmjs.org':
        raise ValueError('只允許從官方 npm 登錄庫讀取固定版本套件')
    with urlopen(Request(url, headers={'User-Agent': 'n8n-zh-tw-static-catalog'}), timeout=60) as response:
        data = response.read(limit + 1)
    if len(data) > limit:
        raise ValueError('來源超過大小限制')
    return data


def catalog(package, version):
    meta = json.loads(get(f'https://registry.npmjs.org/{quote(package, safe="")}/{quote(version, safe="")}', 2_000_000))
    if meta.get('name') != package or meta.get('version') != version:
        raise ValueError('套件名稱或版本不符')
    data = get(meta['dist']['tarball'], 120_000_000)
    integrity = meta['dist'].get('integrity', '')
    if not integrity.startswith('sha512-'):
        raise ValueError('來源未提供預期的 SHA-512 完整性資訊')
    actual = base64.b64encode(hashlib.sha512(data).digest()).decode()
    if actual != integrity[len('sha512-'):]:
        raise ValueError('套件完整性檢查失敗')
    # 不 extract、不匯入 JS；只在記憶體讀取三個固定路徑的 JSON。
    result = {}
    with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as archive:
        for kind in ('nodes', 'credentials'):
            member = archive.getmember(f'package/dist/types/{kind}.json')
            if not member.isfile() or member.size > 65_000_000:
                raise ValueError('節點描述不是允許的 JSON 檔案')
            handle = archive.extractfile(member)
            result[kind] = json.load(handle)
            if not isinstance(result[kind], list):
                raise ValueError('未預期的套件描述格式')
    return result, {'package': package, 'version': version, 'integrity': integrity,
                    'tarball': meta['dist']['tarball'], 'source': 'official npm static JSON only'}


def valid_key(value):
    return isinstance(value, str) and bool(value) and value not in BAD_KEYS


def collect_properties(properties, prefix, collect):
    if not isinstance(properties, list):
        return
    for prop in properties:
        if not isinstance(prop, dict) or not valid_key(prop.get('name')):
            continue
        path = prefix + prop['name']
        for field in TEXT_FIELDS:
            if isinstance(prop.get(field), str):
                collect(path + '.' + field, prop[field])
        options = prop.get('options', [])
        if prop.get('type') in ('options', 'multiOptions') and isinstance(options, list):
            for option in options:
                if not isinstance(option, dict) or not isinstance(option.get('value'), (str, int, float, bool)):
                    continue
                value = option['value']
                key = str(value).lower() if isinstance(value, bool) else str(value)
                if not valid_key(key):
                    continue
                for source_field, target_field in [('name', 'displayName'), ('description', 'description')]:
                    if isinstance(option.get(source_field), str):
                        collect(path + '.options.' + key + '.' + target_field, option[source_field])
        elif prop.get('type') == 'collection':
            collect_properties(options, path + '.options.', collect)
        elif prop.get('type') == 'fixedCollection' and isinstance(options, list):
            for option in options:
                if not isinstance(option, dict) or not valid_key(option.get('name')):
                    continue
                option_path = path + '.options.' + option['name']
                if isinstance(option.get('displayName'), str):
                    collect(option_path + '.displayName', option['displayName'])
                collect_properties(option.get('values', []), option_path + '.values.', collect)
        type_options = prop.get('typeOptions', {})
        if isinstance(type_options, dict):
            for field in ('multipleValueButtonText', 'addOptionalFieldButtonText'):
                if isinstance(type_options.get(field), str):
                    collect(path + '.' + field, type_options[field])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output / 'localization/zh-TW'
    memory = read_json(out / 'phrase-memory.json')
    en, _ = read_source(args.root / 'packages/frontend/@n8n/i18n/src/locales/en.json')
    translated = read_json(args.output / 'packages/frontend/@n8n/i18n/src/locales/zh-TW.json')
    base_translations = defaultdict(set)
    original_leaves, translated_leaves = leaves(en), leaves(translated)
    for key, source in original_leaves.items():
        if key in translated_leaves and CJK.search(translated_leaves[key]):
            base_translations[source].add(translated_leaves[key])
    for source, values in base_translations.items():
        if len(values) == 1:
            memory[source] = next(iter(values))
    report = {'native_complete': False, 'production_ready': False,
              'strategy': 'exact source matching; ambiguous version/operation paths omitted; no node JS executed', 'packages': []}
    for package, manifest_path in PACKAGES.items():
        manifest = read_json(args.root / manifest_path)
        version = manifest['version']
        filename = 'nodes-base.json' if package == 'n8n-nodes-base' else 'nodes-langchain.json'
        target = {}
        package_report = {'package': package, 'version': version, 'status': 'not-generated'}
        try:
            descriptions, provenance = catalog(package, version)
            sources = defaultdict(set)

            def collect(key, text):
                sources[key].add(text)

            node_names = set()
            for node in descriptions['nodes']:
                if not isinstance(node, dict) or not valid_key(node.get('name')):
                    continue
                name = node['name']
                prefix = package + '.'
                short_name = name[len(prefix):] if name.startswith(prefix) else name
                if package != 'n8n-nodes-base':
                    short_name = prefix + short_name
                node_names.add(short_name)
                for field in ('displayName', 'description'):
                    if isinstance(node.get(field), str):
                        collect(f'headers.{short_name}.{field}', node[field])
                node_prefix = f'n8n-nodes-base.nodes.{short_name}.nodeView.'
                if isinstance(node.get('eventTriggerDescription'), str):
                    collect(node_prefix + 'eventTriggerDescription', node['eventTriggerDescription'])
                collect_properties(node.get('properties', []), node_prefix, collect)
            credential_names = set()
            for credential in descriptions['credentials']:
                if not isinstance(credential, dict) or not valid_key(credential.get('name')):
                    continue
                name = credential['name']
                credential_names.add(name)
                collect_properties(credential.get('properties', []), f'n8n-nodes-base.credentials.{name}.', collect)
            missing, conflicts = [], []
            for key, originals in sorted(sources.items()):
                candidates = set()
                for original in originals:
                    candidate = memory.get(original)
                    if candidate is None and retained_reason((key,), original):
                        candidate = original
                    if candidate is not None and not structural_errors(original, candidate):
                        if CJK.search(candidate) or retained_reason((key,), original):
                            candidates.add(candidate)
                        else:
                            candidates.add(None)
                    else:
                        candidates.add(None)
                if None not in candidates and len(candidates) == 1:
                    target[key] = next(iter(candidates))
                elif len(originals) > 1:
                    conflicts.append({'key': key, 'sources': sorted(originals)})
                else:
                    missing.append({'key': key, 'source': next(iter(originals))})
            package_report.update(provenance)
            package_report.update({'status': 'candidate', 'node_types': len(node_names),
                                  'credential_types': len(credential_names), 'message_paths': len(sources),
                                  'provided': len(target), 'missing_count': len(missing),
                                  'ambiguous_paths_count': len(conflicts), 'missing': missing, 'ambiguous_paths': conflicts})
        except (HTTPError, OSError, ValueError, KeyError, tarfile.TarError) as error:
            package_report['status'] = 'unavailable'
            package_report['error'] = str(error)
        directory = out / 'native'
        directory.mkdir(parents=True, exist_ok=True)
        (directory / filename).write_text(json.dumps(target, ensure_ascii=False, indent='\t') + '\n', encoding='utf-8')
        report['packages'].append(package_report)
        print('NATIVE_CATALOG=' + json.dumps({k: v for k, v in package_report.items() if k not in {'missing', 'ambiguous_paths'}}, ensure_ascii=False))
    (out / 'native-coverage.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
