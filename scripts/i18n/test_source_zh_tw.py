"""確認上游重複鍵不被暗中修改，且目標語言檔仍嚴格拒絕重複鍵。"""
from pathlib import Path
import tempfile
import unittest

import validate_zh_tw as validator


class SourceDuplicateTests(unittest.TestCase):
    def test_source_duplicates_are_reported_and_last_value_is_used(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'en.json'
            original = '{"key":"Old","key":"New"}'
            path.write_text(original, encoding='utf-8')
            data, duplicates = validator.read_source(path)
            self.assertEqual(data, {'key': 'New'})
            self.assertEqual(duplicates, [{'key': 'key', 'same_value': False}])
            self.assertEqual(path.read_text(encoding='utf-8'), original)

    def test_identical_source_duplicates_are_still_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'en.json'
            path.write_text('{"key":"Same","key":"Same"}', encoding='utf-8')
            _, duplicates = validator.read_source(path)
            self.assertEqual(duplicates, [{'key': 'key', 'same_value': True}])

    def test_translation_duplicates_always_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'zh-TW.json'
            path.write_text('{"key":"儲存","key":"儲存"}', encoding='utf-8')
            with self.assertRaises(ValueError):
                validator.read_json(path)


if __name__ == '__main__':
    unittest.main()
