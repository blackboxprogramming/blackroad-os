#!/usr/bin/env node

import { execFileSync } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const validators = [
  { script: 'validate-registry.mjs', name: 'Product Registry' },
  { script: 'validate-agents.mjs', name: 'Agent Registry' },
  { script: 'validate-agents-roster.mjs', name: 'Agent Roster' },
  { script: 'validate-glovebox.mjs', name: 'GloveBox Tools' },
  { script: 'validate-roadchain.mjs', name: 'RoadChain Ledger' },
  { script: 'validate-collections.mjs', name: 'Collections' },
  { script: 'validate-references.mjs', name: 'Cross-Registry References' },
  { script: 'sync-products.mjs', args: ['--check'], name: 'Generated Products' },
  { script: 'sync-collections.mjs', args: ['--check'], name: 'Generated Collections' },
  { script: 'sync-product-folders.mjs', args: ['--check'], name: 'Product Folders' }
];

console.log('🔍 Running full BlackRoad OS validation suite...\n');

let failed = [];
let passed = [];

for (const validator of validators) {
  try {
    console.log(`📋 Validating ${validator.name}...`);
    execFileSync(process.execPath, [path.join(__dirname, validator.script), ...(validator.args ?? [])], { stdio: 'pipe' });
    passed.push(validator.name);
    console.log(`   ✓ Passed\n`);
  } catch (error) {
    failed.push(validator.name);
    console.log(`   ✗ Failed\n`);
    if (error.stdout) process.stdout.write(error.stdout);
    if (error.stderr) process.stderr.write(error.stderr);
  }
}

console.log('\n' + '='.repeat(50));
console.log(`Results: ${passed.length} passed, ${failed.length} failed`);

if (failed.length > 0) {
  console.log('\n❌ Failed validators:');
  failed.forEach(name => console.log(`  - ${name}`));
  process.exit(1);
} else {
  console.log('\n✨ All validators passed!');
  process.exit(0);
}
