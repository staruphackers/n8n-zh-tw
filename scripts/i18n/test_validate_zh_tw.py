"""繁中語言包驗證器的離線測試，不執行 n8n 或連線至正式主機。"""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest

import validate_zh_tw as validator


class LocalizationValidationTests(unittest.TestCase):
    def test_valid_translation(self):
        self.assertEqual(validator.structural_errors('Open {resource}', '開啟 {resource}'), [])

    def test_missing_placeholder(self):
        self.assertTrue(validator.structural_errors('Open {resource}', '開啟'))

    def test_repeated_placeholder(self):
        self.assertTrue(validator.structural_errors('{name}: {name}', '{name}'))

    def test_plural_branches_preserved(self):
        self.assertEqual(validator.structural_errors('Folder | {count} Folder | {count} Folders', '資料夾 | {count} 個資料夾 | {count} 個資料夾'), [])

    def test_plural_branch_cannot_be_dropped(self):
        self.assertTrue(validator.structural_errors('Folder | {count} Folders', '{count} 個資料夾'))

    def test_placeholder_cannot_move_between_branches(self):
        self.assertTrue(validator.structural_errors('One | {count} items', '{count} 個 | 一個'))

    def test_literal_pipe(self):
        self.assertEqual(validator.branches("Use {'|'} here | other"), ["Use {'|'} here ", ' other'])

    def test_link_reference(self):
        self.assertEqual(validator.structural_errors('@:_reusableBaseText.save', '@:_reusableBaseText.save'), [])
        self.assertTrue(validator.structural_errors('@:_reusableBaseText.save', '@:_reusableBaseText.cancel'))

    def test_code_cannot_change(self):
        self.assertTrue(validator.structural_errors('Use `$json`', '使用 `$資料`'))
        self.assertTrue(validator.structural_errors('Use <code>item.json</code>', '使用 <code>item.data</code>'))

    def test_url_cannot_change(self):
        self.assertTrue(validator.structural_errors('See https://docs.n8n.io/', '參閱 https://example.com/'))

    def test_html_text_and_title_can_translate(self):
        self.assertEqual(validator.structural_errors('<a href="{url}" target="_blank" title="Read docs">More</a>', '<a href="{url}" target="_blank" title="閱讀文件">更多</a>'), [])

    def test_html_link_and_attribute_injection_rejected(self):
        self.assertTrue(validator.structural_errors('<a href="{url}">More</a>', '<a href="{url}" onclick="alert(1)">更多</a>'))
        self.assertTrue(validator.structural_errors('<a href="/settings">More</a>', '<a href="/admin">更多</a>'))

    def test_html_tag_change_rejected(self):
        self.assertTrue(validator.structural_errors('<strong>Warning</strong>', '<em>警告</em>'))

    def test_empty_translation_rejected(self):
        self.assertTrue(validator.structural_errors('Save', ' '))

    def test_nested_and_dotted_keys_are_distinct(self):
        data = validator.leaves({'a.b': 'Save', 'a': {'b': 'Open'}})
        self.assertEqual(len(data), 2)
        self.assertIn(('a.b',), data)
        self.assertIn(('a', 'b'), data)

    def test_nonstring_values_rejected(self):
        with self.assertRaises(ValueError):
            validator.leaves({'save': False})

    def test_duplicate_keys_rejected(self):
        with self.assertRaises(ValueError):
            json.loads('{"save":"儲存","save":"保存"}', object_pairs_hook=validator.reject_duplicates)

    def test_missing_extra_and_untranslated_are_reported(self):
        report = validator.inspect({'save': 'Save', 'open': 'Open'}, {'save': 'Save', 'extra': '額外'})
        self.assertEqual(report['missing_count'], 1)
        self.assertEqual(report['extra_count'], 1)
        self.assertEqual(report['untranslated_or_review_count'], 1)
        self.assertFalse(report['base_text_complete'])
        self.assertFalse(report['production_ready'])

    def test_technical_terms_and_references_are_not_fake_translations(self):
        data = {'generic.pro': 'Pro', 'format': '{count}/{max}', 'role': '@:_reusableBaseText.roles.admin'}
        report = validator.inspect(data, data)
        self.assertEqual(report['retained_technical_or_reference_count'], 3)
        self.assertEqual(report['changed_or_localized_count'], 0)
        self.assertFalse(report['production_ready'])

    def test_partial_mode_still_rejects_corruption(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            locale_dir = root / validator.LOCALE_DIR
            locale_dir.mkdir(parents=True)
            (locale_dir / 'en.json').write_text(json.dumps({'save': 'Save', 'open': 'Open {name}'}), encoding='utf-8')
            (locale_dir / 'zh-TW.json').write_text(json.dumps({'save': '儲存'}), encoding='utf-8')
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(validator.main(['--root', str(root)]), 1)
                self.assertEqual(validator.main(['--root', str(root), '--allow-partial']), 0)
                (locale_dir / 'zh-TW.json').write_text(json.dumps({'open': '開啟'}), encoding='utf-8')
                self.assertEqual(validator.main(['--root', str(root), '--allow-partial']), 1)


if __name__ == '__main__':
    unittest.main()
