#!/usr/bin/env node

import fs from 'fs';
import path from 'path';
import crypto from 'crypto';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const registryDir = path.join(__dirname, '..', 'Registry');

async function validateRoadChain() {
  console.log('⛓️  Validating RoadChain receipt ledger...\n');

  try {
    const receiptData = JSON.parse(fs.readFileSync(path.join(registryDir, 'roadchain-receipts.json'), 'utf8'));

    if (!receiptData.receipts || receiptData.receipts.length === 0) {
      console.log('⚠️  Receipt ledger is empty');
      process.exit(0);
    }

    let priorHash = receiptData.genesis_hash;
    let validReceipts = 0;
    let errors = 0;

    console.log(`📜 Validating ${receiptData.receipts.length} receipts...\n`);

    for (let i = 0; i < receiptData.receipts.length; i++) {
      const receipt = receiptData.receipts[i];

      // Check required fields
      if (!receipt.receipt_id || !receipt.timestamp || !receipt.subject || !receipt.action || !receipt.product) {
        console.error(`❌ Receipt ${i} missing required fields`);
        errors++;
        continue;
      }

      // Check prior_hash chain
      if (receipt.prior_hash !== priorHash) {
        console.error(`❌ Receipt ${i} (${receipt.receipt_id}): chain broken`);
        console.error(`   Expected prior_hash: ${priorHash}`);
        console.error(`   Actual prior_hash: ${receipt.prior_hash}`);
        errors++;
      }

      // Verify receipt_id format
      if (!/^REC-\d{4}-[A-Z0-9]{8}$/.test(receipt.receipt_id)) {
        console.warn(`⚠️  Receipt ${i}: malformed ID ${receipt.receipt_id}`);
      }

      // Check valid action types
      const validActions = [
        'OPERATOR_SET', 'OPERATOR_HANDOFF', 'PRODUCT_LAUNCHED', 'PRODUCT_DEPLOYED',
        'AGENT_ASSIGNED', 'AGENT_COMPLETED', 'TOOL_EXECUTED', 'TOOL_GRANTED',
        'CARKEYS_APPROVED', 'CARKEYS_REVOKED', 'MODEL_INFERENCE', 'DATA_EXPORTED',
        'RECEIPT_VERIFIED'
      ];
      if (!validActions.includes(receipt.action)) {
        console.warn(`⚠️  Receipt ${i}: unknown action ${receipt.action}`);
      }

      validReceipts++;
      priorHash = receipt.chain_hash;

      if (i < 3 || i === receiptData.receipts.length - 1) {
        console.log(`  ✓ ${receipt.receipt_id}: ${receipt.action} (${receipt.subject})`);
      } else if (i === 3) {
        console.log(`  ... (${receiptData.receipts.length - 4} more receipts) ...`);
      }
    }

    console.log(`\n✅ Valid receipts: ${validReceipts}/${receiptData.receipts.length}`);

    if (errors > 0) {
      console.log(`❌ Errors: ${errors}`);
      console.log('\n⚠️  Chain integrity issues detected');
      process.exit(1);
    } else {
      console.log('\n✨ RoadChain ledger is valid!');
      process.exit(0);
    }
  } catch (error) {
    console.error('❌ Validation failed:', error.message);
    process.exit(1);
  }
}

validateRoadChain();
