import unittest
from retained_zh_tw import retained_reason
from validate_zh_tw import inspect


class RetainedTextTests(unittest.TestCase):
    def test_brand_requires_complete_value(self):
        self.assertIsNotNone(retained_reason(('brand',), 'OpenAI'))
        self.assertIsNone(retained_reason(('brand',), 'Connect to OpenAI'))
        self.assertIsNone(retained_reason(('brand',), 'OpenAI API key is missing'))

    def test_literal_requires_exact_key_and_source(self):
        key = ('chatEmbed.paste.vue.file',)
        self.assertIsNotNone(retained_reason(key, 'App.vue'))
        self.assertIsNone(retained_reason(('other',), 'App.vue'))
        self.assertIsNone(retained_reason(key, 'Change App.vue'))

    def test_changed_english_cannot_pass_as_brand(self):
        result = inspect({'x': 'Save'}, {'x': 'OpenAI'})
        self.assertEqual(result['untranslated_or_review_count'], 1)
        self.assertFalse(result['base_text_complete'])

    def test_explicit_format_is_auditable(self):
        source = {'dataTable.card.size': '{size}MB'}
        result = inspect(source, source)
        self.assertTrue(result['base_text_complete'])
        self.assertEqual(result['retained_technical_or_reference_count'], 1)
        self.assertIn('核准', result['retained'][0]['reason'])
        self.assertFalse(result['production_ready'])


if __name__ == '__main__':
    unittest.main()
