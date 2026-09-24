'use strict';
const fs = require('node:fs');
const path = require('node:path');
const { createRequire } = require('node:module');
const dependencyDirectory = process.argv[2];
const output = process.argv[3];
if (!dependencyDirectory || !output) throw new Error('請提供依賴及候選產物目錄');
const requireDependency = createRequire(path.resolve(dependencyDirectory, 'package.json'));
const { baseCompile } = requireDependency('@intlify/message-compiler');
const directory = path.join(output, 'localization/zh-TW');
const reportPath = path.join(directory, 'native-coverage.json');
const report = JSON.parse(fs.readFileSync(reportPath, 'utf8'));
for (const [index, filename] of ['nodes-base.json', 'nodes-langchain.json'].entries()) {
  const file = path.join(directory, 'native', filename);
  const messages = JSON.parse(fs.readFileSync(file, 'utf8'));
  const rejected = [];
  for (const [key, value] of Object.entries(messages)) {
    const errors = [];
    baseCompile(value, { onError: (error) => errors.push(error.message) });
    if (errors.length) {
      rejected.push({ key, errors });
      delete messages[key];
    }
  }
  fs.writeFileSync(file, JSON.stringify(messages, null, '\t') + '\n');
  Object.assign(report.packages[index], {
    provided_after_message_compilation: Object.keys(messages).length,
    message_compilation_rejected_count: rejected.length,
    message_compilation_rejected: rejected,
  });
  console.log('NATIVE_MESSAGE_COMPILE=' + JSON.stringify({ file: filename, compiled: Object.keys(messages).length, rejected: rejected.length }));
}
fs.writeFileSync(reportPath, JSON.stringify(report, null, 2) + '\n');
