#!/usr/bin/env node

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.join(__dirname, '..');
const registryDir = path.join(rootDir, 'Registry');
const productsDir = path.join(rootDir, 'Products');

async function syncGloveBox() {
  const checkOnly = process.argv.includes('--check');

  console.log(`${checkOnly ? '✓ Checking' : '🔧 Syncing'} GloveBox registry...\n`);

  try {
    const toolsData = JSON.parse(fs.readFileSync(path.join(registryDir, 'glovebox-tools.json'), 'utf8'));

    // For now, just validate that the registry is sound
    if (!toolsData.tools || toolsData.tools.length === 0) {
      console.error('❌ No tools found in GloveBox registry');
      process.exit(1);
    }

    console.log(`✓ GloveBox registry has ${toolsData.tools.length} tools`);

    // Check that all product tool references are valid
    const toolIds = new Set(toolsData.tools.map(t => t.id));
    let productErrors = 0;

    for (const productFolder of fs.readdirSync(productsDir)) {
      if (!fs.statSync(path.join(productsDir, productFolder)).isDirectory()) continue;

      const toolsJsonPath = path.join(productsDir, productFolder, 'tools.json');
      if (!fs.existsSync(toolsJsonPath)) continue;

      const productTools = JSON.parse(fs.readFileSync(toolsJsonPath, 'utf8'));
      for (const tool of productTools.tools_used || []) {
        if (!toolIds.has(tool.tool_id)) {
          console.warn(`⚠️  ${productFolder}: tool ${tool.tool_id} not in GloveBox registry`);
          productErrors++;
        }
      }
    }

    if (productErrors > 0) {
      console.log(`\n⚠️  Found ${productErrors} tool reference mismatches`);
    }

    console.log('\n✨ GloveBox sync complete!');
    process.exit(productErrors > 0 ? 1 : 0);
  } catch (error) {
    console.error('❌ Sync failed:', error.message);
    process.exit(1);
  }
}

syncGloveBox();
