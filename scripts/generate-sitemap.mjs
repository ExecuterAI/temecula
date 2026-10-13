import { readFileSync, writeFileSync, readdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const origin = 'https://bellieacreswine.com';
const today = new Date().toISOString().slice(0, 10);

const wineries = JSON.parse(readFileSync(join(root, 'src/data/wineries.json'), 'utf8'));
const guideDir = join(root, 'src/pages/guides');
const guides = readdirSync(guideDir)
  .filter((name) => name.endsWith('.astro') && name !== 'index.astro')
  .map((name) => `/guides/${name.replace(/\.astro$/, '')}/`)
  .sort();

const hubs = [
  ['/', 'weekly', '1.0'],
  ['/wineries/', 'weekly', '0.9'],
  ['/guides/', 'weekly', '0.9'],
  ['/map/', 'weekly', '0.8'],
  ['/pairings/', 'weekly', '0.7'],
  ['/balloons/', 'weekly', '0.7'],
  ['/events/', 'weekly', '0.7'],
  ['/collection/', 'weekly', '0.6'],
  ['/wine-day-planner/', 'monthly', '0.7'],
  ['/search/', 'weekly', '0.5'],
  ['/about/', 'monthly', '0.6'],
  ['/contact/', 'monthly', '0.6'],
  ['/privacy/', 'yearly', '0.4'],
  ['/terms/', 'yearly', '0.4'],
  ['/advertise/', 'monthly', '0.5'],
];

const wineryPaths = wineries
  .filter((winery) => typeof winery.perspective === 'string' && winery.perspective.trim())
  .map((winery) => `/wineries/${winery.slug}/`)
  .sort();

const urls = [
  ...hubs.map(([path, changefreq, priority]) => ({ path, changefreq, priority })),
  ...guides.map((path) => ({ path, changefreq: 'monthly', priority: '0.85' })),
  ...wineryPaths.map((path) => ({ path, changefreq: 'monthly', priority: '0.8' })),
];

const seen = new Set();
for (const url of urls) {
  if (!url.path.startsWith('/') || !url.path.endsWith('/')) {
    throw new Error(`Bad path: ${url.path}`);
  }
  if (seen.has(url.path)) throw new Error(`Duplicate path: ${url.path}`);
  seen.add(url.path);
}

const excluded = ['/wineries/frangipani/', '/wineries/temecula-creek/', '/weekend-planner/'];
for (const path of excluded) {
  if ([...seen].some((item) => item.includes(path))) {
    throw new Error(`Noindex path slipped in: ${path}`);
  }
}

function urlset(entries) {
  const body = entries
    .map(
      (url) => `  <url>
    <loc>${origin}${url.path}</loc>
    <lastmod>${today}</lastmod>
    <changefreq>${url.changefreq}</changefreq>
    <priority>${url.priority}</priority>
  </url>`
    )
    .join('\n');
  return `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${body}
</urlset>
`;
}

const xml = urlset(urls);
writeFileSync(join(root, 'public/sitemap.xml'), xml);
writeFileSync(join(root, 'public/sitemap-temecula.xml'), xml);
writeFileSync(
  join(root, 'public/sitemap_index.xml'),
  `<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap>
    <loc>${origin}/sitemap.xml</loc>
    <lastmod>${today}</lastmod>
  </sitemap>
  <sitemap>
    <loc>${origin}/sitemap-temecula.xml</loc>
    <lastmod>${today}</lastmod>
  </sitemap>
</sitemapindex>
`
);
console.log(`sitemap ${today} urls=${urls.length} wineries=${wineryPaths.length} guides=${guides.length}`);
