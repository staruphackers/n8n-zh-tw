import unittest
from generate_native_zh_tw import collect_properties, valid_key


class NativeTranslationTests(unittest.TestCase):
    def collect(self, properties):
        result = {}
        collect_properties(properties, 'node.', lambda key, value: result.__setitem__(key, value))
        return result

    def test_only_display_fields(self):
        source = [{'name': 'token', 'displayName': 'Access Token', 'type': 'string',
                   'description': 'Secret', 'default': 'DO_NOT_TRANSLATE',
                   'displayOptions': {'show': {'operation': ['send']}}}]
        result = self.collect(source)
        self.assertEqual(result, {'node.token.displayName': 'Access Token', 'node.token.description': 'Secret'})
        self.assertEqual(source[0]['default'], 'DO_NOT_TRANSLATE')

    def test_options_keep_original_value_keys(self):
        result = self.collect([{'name': 'action', 'type': 'options', 'options': [
            {'name': 'Create', 'value': 'createObject', 'description': 'Create object'}]}])
        self.assertEqual(result['node.action.options.createObject.displayName'], 'Create')
        self.assertNotIn('node.action.options.Create.displayName', result)

    def test_boolean_option_key_uses_json_case(self):
        result = self.collect([{'name': 'enabled', 'type': 'options', 'options': [{'name': 'Yes', 'value': True}]}])
        self.assertIn('node.enabled.options.true.displayName', result)

    def test_nested_fixed_collection(self):
        result = self.collect([{'name': 'headers', 'type': 'fixedCollection', 'options': [
            {'name': 'header', 'displayName': 'Header', 'values': [{'name': 'name', 'displayName': 'Name', 'type': 'string'}]}]}])
        self.assertIn('node.headers.options.header.values.name.displayName', result)

    def test_collection_and_button_text(self):
        result = self.collect([{'name': 'options', 'type': 'collection',
            'typeOptions': {'multipleValueButtonText': 'Add option'},
            'options': [{'name': 'timeout', 'displayName': 'Timeout', 'type': 'number'}]}])
        self.assertIn('node.options.options.timeout.displayName', result)
        self.assertEqual(result['node.options.multipleValueButtonText'], 'Add option')

    def test_unsafe_keys_rejected(self):
        for name in ('__proto__', 'constructor', 'prototype', ''):
            self.assertFalse(valid_key(name))
            self.assertEqual(self.collect([{'name': name, 'displayName': 'Unsafe'}]), {})


if __name__ == '__main__':
    unittest.main()
