'use strict';
// 隔離測試實際 i18n 原始碼，不啟動 n8n、不讀取資料庫或正式環境。
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { createRequire } = require('node:module');

async function main() {
  const dependencyDirectory = process.argv[2];
  const root = path.resolve(process.argv[3] || '.');
  if (!dependencyDirectory) throw new Error('請提供隔離測試依賴目錄');
  const dependencyRequire = createRequire(path.resolve(dependencyDirectory, 'package.json'));
  const { build } = dependencyRequire('esbuild');
  const { baseCompile } = dependencyRequire('@intlify/message-compiler');
  const localeDirectory = path.join(root, 'packages/frontend/@n8n/i18n/src/locales');
  const english = JSON.parse(fs.readFileSync(path.join(localeDirectory, 'en.json'), 'utf8'));
  const traditional = JSON.parse(fs.readFileSync(path.join(localeDirectory, 'zh-TW.json'), 'utf8'));
  function flatten(value, prefix = []) {
    return Object.entries(value).flatMap(([key, item]) => typeof item === 'string'
      ? [{ key: [...prefix, key], value: item }]
      : flatten(item, [...prefix, key]));
  }
  const syntaxErrors = [];
  const entries = flatten(traditional);
  for (const entry of entries) {
    baseCompile(entry.value, {
      onError: (error) => syntaxErrors.push({ key: entry.key, message: error.message }),
    });
  }
  if (syntaxErrors.length) {
    console.error('繁中訊息編譯錯誤：', JSON.stringify(syntaxErrors, null, 2));
    throw new Error(`${syntaxErrors.length} 項訊息編譯錯誤`);
  }
  console.log(`PASS ${entries.length} 筆繁中訊息語法編譯`);
  const output = path.resolve(dependencyDirectory, 'n8n-i18n-under-test.cjs');
  await build({
    entryPoints: [path.join(root, 'packages/frontend/@n8n/i18n/src/index.ts')],
    outfile: output,
    bundle: true,
    platform: 'node',
    format: 'cjs',
    tsconfigRaw: { compilerOptions: { target: 'ES2022' } },
    nodePaths: [path.resolve(dependencyDirectory, 'node_modules')],
    logLevel: 'warning',
  });
  // 先在 Node.js 環境載入 Vue；本測試不模擬完整 DOM，也不呼叫 Vue 畫面渲染。
  const { i18n, i18nInstance, setLanguage, addNodeTranslation, addCredentialTranslation, addHeaders } = require(output);
  let htmlLanguage;
  global.document = {
    querySelector: (selector) => {
      assert.equal(selector, 'html');
      return { setAttribute: (name, value) => { assert.equal(name, 'lang'); htmlLanguage = value; } };
    },
  };
  const check = (name, fn) => { fn(); console.log(`PASS ${name}`); };
  check('保留英文預設', () => {
    assert.equal(i18n.locale, 'en');
    assert.equal(i18n.baseText('generic.save'), english['generic.save']);
  });
  check('zh-TW 註冊與 HTML 語言', () => {
    setLanguage('zh-TW');
    assert.equal(htmlLanguage, 'zh-TW');
    assert.equal(i18n.baseText('generic.save'), '儲存');
    assert.equal(i18n.baseText('auth.signin'), '登入');
  });
  check('具名字串插值', () => {
    assert.equal(i18n.baseText('generic.openResource', { interpolate: { resource: '測試工作流程' } }), '開啟 測試工作流程');
  });
  check('複數分支', () => {
    assert.equal(i18n.baseText('generic.workflow', { adjustToNumber: 2, interpolate: { count: 2 } }), '2 個工作流程');
  });
  check('共用文字參照', () => {
    assert.equal(i18n.baseText('auth.roles.admin'), '管理員');
  });
  check('缺少文字時仍保留英文備援', () => {
    i18nInstance.global.mergeLocaleMessage('en', { '__zh_tw_test_fallback': 'Keep original fallback' });
    assert.equal(i18nInstance.global.t('__zh_tw_test_fallback'), 'Keep original fallback');
  });
  check('節點與憑證翻譯可透過既有介面加入', () => {
    addNodeTranslation({ localizationTest: { nodeView: { value: { displayName: '測試欄位' } } } }, 'zh-TW');
    addCredentialTranslation({ localizationTest: { token: { displayName: '測試權杖' } } }, 'zh-TW');
    addHeaders({ localizationTest: { displayName: '測試節點', description: '測試說明' } }, 'zh-TW');
    assert.equal(i18n.nodeText('n8n-nodes-base.localizationTest').inputLabelDisplayName({ name: 'value', displayName: 'Original value', type: 'string' }, 'parameters.value'), '測試欄位');
    assert.equal(i18n.credText('localizationTest').inputLabelDisplayName({ name: 'token', displayName: 'Original token' }), '測試權杖');
    assert.equal(i18n.localizeNodeName('zh-TW', 'Original node', 'n8n-nodes-base.localizationTest'), '測試節點');
  });
  check('未翻譯的節點原文與使用者名稱不被改寫', () => {
    assert.equal(i18n.nodeText('n8n-nodes-base.unknownForTest').inputLabelDisplayName({ name: 'value', displayName: 'User/API value', type: 'string' }, 'parameters.value'), 'User/API value');
  });
  check('切回英文會清除舊語系快取', () => {
    setLanguage('en');
    assert.equal(i18n.baseText('generic.save'), english['generic.save']);
    setLanguage('zh-TW');
    assert.equal(i18n.baseText('generic.save'), '儲存');
  });
  console.log(JSON.stringify({ compiled_messages: entries.length, runtime_checks: 9, browser_e2e: false, full_n8n_build: false, production_deployment: false }));
}
main().catch((error) => { console.error(error); process.exitCode = 1; });
