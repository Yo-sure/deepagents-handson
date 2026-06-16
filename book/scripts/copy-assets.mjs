// books/images → book/public/images 복사 (Obsidian 임베드 이미지가 정적 빌드에 포함되도록)
import { cp, mkdir, readdir } from 'node:fs/promises'
import { existsSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, resolve } from 'node:path'

const __dirname = dirname(fileURLToPath(import.meta.url))
const src = resolve(__dirname, '../../books/images')
const dst = resolve(__dirname, '../public/images')

if (!existsSync(src)) {
  console.warn(`[copy-assets] 원본 없음(건너뜀): ${src}`)
  process.exit(0)
}
await mkdir(dst, { recursive: true })
await cp(src, dst, { recursive: true })
const n = (await readdir(dst)).length
console.log(`[copy-assets] ${n}개 항목 복사: books/images → book/public/images`)
