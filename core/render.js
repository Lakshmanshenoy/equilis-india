function formatValue(value) {
  if (Array.isArray(value)) {
    return value.length ? value.map((item) => `- ${item}`).join('\n') : 'None';
  }

  if (value && typeof value === 'object') {
    const entries = Object.entries(value);
    return entries.length
      ? entries.map(([key, entryValue]) => `- ${key}: ${entryValue}`).join('\n')
      : 'None';
  }

  return value ? String(value) : 'None';
}

export function renderReportMarkdown(payload, promptModule) {
  const title = payload.company || 'Unnamed Company';
  const summary = payload.summary || 'Unable to verify';
  const financials = formatValue(payload.financials);
  const valuation = formatValue(payload.valuation);
  const risks = formatValue(payload.risks);
  const assumptions = formatValue(payload.assumptions);

  return [
    `# ${title}`,
    '',
    `## Report Context`,
    `- Analysis type: ${promptModule}`,
    `- Ticker: ${payload.ticker || 'Unable to verify'}`,
    `- Generated for educational use only`,
    '',
    `## Summary`,
    summary,
    '',
    `## Financials`,
    financials,
    '',
    `## Valuation`,
    valuation,
    '',
    `## Risks`,
    risks,
    '',
    `## Assumptions`,
    assumptions,
    '',
    `## Disclaimer`,
    `This report is educational and informational only. It does not contain investment advice.`,
    ''
  ].join('\n');
}