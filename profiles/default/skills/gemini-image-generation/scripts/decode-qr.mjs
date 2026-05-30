#!/usr/bin/env node
/**
 * decode-qr.mjs — Decode a QR code image to text
 *
 * Usage:
 *   node decode-qr.mjs <image_path>
 *
 * Dependencies (install once):
 *   npm install jsqr jimp
 *
 * This is a pure-JS QR decoder that works when zbarimg/pyzbar
 * are not available (e.g. in WSL without sudo for apt packages).
 */

import jsQR from 'jsqr';
import { Jimp } from 'jimp';

const inputPath = process.argv[2];
if (!inputPath) {
  console.error('Usage: node decode-qr.mjs <image_path>');
  process.exit(1);
}

try {
  const image = await Jimp.read(inputPath);
  const { data, width, height } = image.bitmap;

  // jsQR expects Uint8ClampedArray
  const code = jsQR(new Uint8ClampedArray(data), width, height);

  if (code) {
    console.log(code.data);
    console.error('✓ QR code decoded successfully');
  } else {
    console.error('✗ No QR code found in image');
    process.exit(2);
  }
} catch (err) {
  console.error(`✗ Error reading image: ${err.message}`);
  process.exit(1);
}
