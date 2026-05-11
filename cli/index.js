#!/usr/bin/env node
import fs from 'fs';
import os from 'os';
import path from 'path';
import { run } from '../core/runner.js';

const inputPath = process.argv[2];
const outputDirFlagIndex = process.argv.indexOf('--output-dir');
const outputDir = outputDirFlagIndex > -1 ? process.argv[outputDirFlagIndex + 1] : path.join(os.homedir(), 'Downloads');

if (!inputPath) {
  console.log('Usage: equilis <input.json>');
  process.exit(1);
}

const input = JSON.parse(fs.readFileSync(inputPath, 'utf8'));
const result = run(input);
const safeCompanyName = (input.company || 'equilis-report').replace(/[^a-z0-9]+/gi, '-').replace(/^-+|-+$/g, '').toLowerCase();
const outputFile = path.join(outputDir, `${safeCompanyName}-research-note.md`);

fs.mkdirSync(outputDir, { recursive: true });
fs.writeFileSync(outputFile, result.markdown, 'utf8');

console.log(`Generating report for: ${input.company}`);
console.log(`Prompt module: ${result.promptModule}`);
console.log(`Markdown report written to: ${outputFile}`);
