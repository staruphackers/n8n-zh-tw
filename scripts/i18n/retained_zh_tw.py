"""僅以完整字串或精確鍵值核准保留原文；不是漏譯豁免。"""
BRANDS_AND_PROTOCOLS = frozenset({
    'Enterprise', 'Pro', 'Sustainable Use License + n8n Enterprise License',
    'n8n', 'n8n AI', 'n8n API', 'AI', 'API', 'ID', 'MCP', 'Slack', 'Telegram',
    'Linear', 'Discord', 'webhook', 'Webhook', 'OAuth1 API', 'OAuth2 API',
    'OAuth2 JWKS URI', 'OpenAI', 'Anthropic', 'Google Gemini', 'MiniMax',
    'Moonshot', 'Qwen Cloud', 'Firecrawl', 'Browserbase', 'Brave Search',
    'PDF.co', 'LlamaIndex', 'CI/CD', 'JSON', 'OpenTelemetry', 'HTTP (protobuf)',
    'gRPC', 'Claude', 'Claude Code', 'Cursor', 'Codex', 'ChatGPT', 'Sentry',
    'Redis', 'Syslog', 'Markdown', 'LDAP', 'XML', 'Google Chrome', 'SearXNG',
    'CSV', 'PDF', 'TXT', 'Mac', 'Windows', 'Linux',
})
# 範例與單位僅在指定鍵名及原文完全一致時保留，來源改寫後必須重新審閱。
EXACT_LITERALS = {
    'chatEmbed.paste.vue.file': 'App.vue',
    'chatEmbed.paste.react.file': 'App.ts',
    'chatEmbed.paste.other.file': 'main.ts',
    'expressionModalInput.null': 'null',
    'settings.opentelemetry.exporterServiceName.placeholder': 'n8n-production',
    'settings.opentelemetry.exporterTracingPath.placeholder': '/v1/traces',
    'settings.sourceControl.sshRepoUrlPlaceholder': "git{'@'}github.com:user/repository.git",
    'dataTable.card.size': '{size}MB',
    'settings.ldap.form.baseDn.placeholder': 'o=acme,dc=example,dc=com',
    'settings.ldap.form.adminDn.placeholder': 'uid=2da2de69435c,ou=Users,o=Acme,dc=com',
    'settings.ldap.form.userFilter.placeholder': '(ObjectClass=user)',
    'settings.ldap.form.ldapId.placeholder': 'uid',
    'settings.ldap.form.loginId.placeholder': 'mail',
    'settings.ldap.form.email.placeholder': 'mail',
    'settings.ldap.form.firstName.placeholder': 'givenName',
    'settings.ldap.form.lastName.placeholder': 'sn',
    'settings.sso.settings.roleMappingRules.expression.placeholder': "$claims.groups.includes('admins')",
    'evaluations.tests.metric.custom.placeholder': '$json.response.length > 1000',
    'agents.builder.files.size.bytes': '{bytes} B',
    'agents.builder.files.size.kilobytes': '{kilobytes} KB',
    'agents.builder.files.size.megabytes': '{megabytes} MB',
    'agents.builder.vectorStores.modal.defaultName': 'new_vector_store',
    'agents.builder.vectorStores.modal.name.placeholder': 'product-docs',
    'agents.builder.vectorStores.modal.indexName.placeholder': 'product-docs',
    'agents.builder.vectorStores.modal.namespace.placeholder': 'production',
    'agents.builder.vectorStores.modal.collectionName.placeholder': 'product-docs',
    'agents.builder.vectorStores.modal.tableName.placeholder': 'documents',
    'agents.builder.vectorStores.modal.queryName.placeholder': 'match_documents',
    'agents.builder.skills.allowedTools.placeholder': 'load_workflow, search_docs',
    'agents.builder.skills.references.name.placeholder': 'reference.md',
}


def retained_reason(key, source):
    if source in BRANDS_AND_PROTOCOLS:
        return '品牌、方案、授權名稱、協定或檔案格式'
    if len(key) == 1 and EXACT_LITERALS.get(key[0]) == source:
        return '已逐項核准的程式識別字、範例或單位格式'
    return None
