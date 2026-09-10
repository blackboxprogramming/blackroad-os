#!/usr/bin/env node

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const registryDir = path.join(__dirname, '..', 'Registry');

async function validateGloveBox() {
  console.log('🔧 Validating GloveBox tool registry...\n');

  try {
    const toolsData = JSON.parse(fs.readFileSync(path.join(registryDir, 'glovebox-tools.json'), 'utf8'));

    // Check total_tools count
    const actualCount = toolsData.tools.length;
    console.log(`📊 Tool count: ${actualCount} (declared: ${toolsData.total_tools})`);

    if (actualCount !== toolsData.total_tools) {
      console.warn(`⚠️  Tool count mismatch: declared ${toolsData.total_tools}, found ${actualCount}`);
      toolsData.total_tools = actualCount; // Auto-fix
      fs.writeFileSync(path.join(registryDir, 'glovebox-tools.json'), JSON.stringify(toolsData, null, 2));
      console.log('✅ Fixed tool count in registry');
    }

    // Validate each tool
    const categories = new Set();
    const toolIds = new Set();
    let validTools = 0;
    let warnings = 0;

    for (const tool of toolsData.tools) {
      // Check required fields
      if (!tool.id || !tool.name || !tool.category || !tool.status) {
        console.error(`❌ Tool missing required fields: ${tool.id}`);
        continue;
      }

      // Check for duplicates
      if (toolIds.has(tool.id)) {
        console.error(`❌ Duplicate tool ID: ${tool.id}`);
        warnings++;
        continue;
      }
      toolIds.add(tool.id);

      // Check category validity
      const validCategories = ['OS', 'Execution', 'Model', 'API', 'Storage', 'Auth', 'Network', 'Media', 'Math', 'Data', 'Crypto'];
      if (!validCategories.includes(tool.category)) {
        console.warn(`⚠️  Unknown category for ${tool.id}: ${tool.category}`);
        warnings++;
      }
      categories.add(tool.category);

      // Check status validity
      const validStatuses = ['REAL', 'MOCK', 'PLANNED'];
      if (!validStatuses.includes(tool.status)) {
        console.error(`❌ Invalid status for ${tool.id}: ${tool.status}`);
        warnings++;
        continue;
      }

      // Check tier range
      if (tool.tier < 0 || tool.tier > 5) {
        console.warn(`⚠️  Tier out of range for ${tool.id}: ${tool.tier}`);
        warnings++;
      }

      validTools++;
    }

    console.log(`\n✅ Valid tools: ${validTools}/${actualCount}`);
    console.log(`📁 Categories: ${Array.from(categories).join(', ')}`);

    if (warnings > 0) {
      console.log(`⚠️  Warnings: ${warnings}`);
    }

    if (validTools === actualCount && warnings === 0) {
      console.log('\n✨ GloveBox registry is valid!');
      process.exit(0);
    } else {
      console.log('\n⚠️  GloveBox registry has issues');
      process.exit(warnings === 0 ? 0 : 1);
    }
  } catch (error) {
    console.error('❌ Validation failed:', error.message);
    process.exit(1);
  }
}

validateGloveBox();
