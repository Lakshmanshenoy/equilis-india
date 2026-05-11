export function validateInput(input) {
  if (!input || typeof input !== 'object') {
    throw new Error('Input must be an object.');
  }

  if (!input.company) {
    throw new Error('Missing required field: company.');
  }

  return true;
}

export function selectPromptModule(analysisType) {
  const modules = {
    financials: 'financial',
    valuation: 'valuation',
    moat: 'moat',
    risk: 'risk',
    sector: 'sector'
  };

  return modules[analysisType] || 'financial';
}

export function buildReportPayload(input) {
  return {
    company: input.company,
    summary: input.summary || '',
    financials: input.financials || {},
    assumptions: input.assumptions || [],
    risks: input.risks || [],
    valuation: input.valuation || {}
  };
}
