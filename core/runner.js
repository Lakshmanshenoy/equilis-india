import { buildReportPayload, selectPromptModule, validateInput } from './pipeline.js';
import { renderReportMarkdown } from './render.js';

export function run(input) {
  validateInput(input);
  const promptModule = selectPromptModule(input.analysisType);
  const payload = buildReportPayload(input);
  const markdown = renderReportMarkdown(payload, promptModule);

  return {
    promptModule,
    payload,
    markdown,
    outputFormat: 'markdown'
  };
}
