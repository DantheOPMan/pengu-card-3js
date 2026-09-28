import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import sharp from 'sharp';

const root = fileURLToPath(new URL('../', import.meta.url));
const source = await readFile(path.join(root, 'public/brand/winter-crown.svg'));
const png = size => sharp(source, { density: 384 }).resize(size, size).png().toBuffer();

await mkdir(path.join(root, 'public/brand'), { recursive: true });
await writeFile(path.join(root, 'public/brand/winter-crown.png'), await png(512));
await writeFile(path.join(root, 'src/app/icon.png'), await png(32));
await sharp(source, { density: 384 }).resize(180, 180)
  .flatten({ background: '#142b3c' }).png().toFile(path.join(root, 'src/app/apple-icon.png'));

// PNG-backed ICO frames keep the same transparent mark crisp at common tab sizes.
const sizes = [16, 32, 48];
const frames = await Promise.all(sizes.map(png));
const header = Buffer.alloc(6 + sizes.length * 16);
header.writeUInt16LE(1, 2);
header.writeUInt16LE(sizes.length, 4);
let offset = header.length;
frames.forEach((frame, index) => {
  const entry = 6 + index * 16;
  header[entry] = header[entry + 1] = sizes[index];
  header.writeUInt16LE(1, entry + 4);
  header.writeUInt16LE(32, entry + 6);
  header.writeUInt32LE(frame.length, entry + 8);
  header.writeUInt32LE(offset, entry + 12);
  offset += frame.length;
});
await writeFile(path.join(root, 'src/app/favicon.ico'), Buffer.concat([header, ...frames]));
console.log('Generated 512px logo, 32px app icon, 180px Apple icon and 16/32/48px favicon.');
