/**
 * DOM extraction. One plugin per site — start with mock site (decision #3, #15);
 * Twitter/Facebook plugins are Phase 4 stretch.
 *
 * Mock-site plugin uses `data-freewall-*` attributes that we control in demo HTML —
 * far more robust than chasing platform CSS classes that change weekly.
 */

export interface ScrapedContent {
  content_id: string
  text: string
  author: string | null
  media_urls: string[]
  source_url: string
  scraped_at: string
}

export interface SitePlugin {
  matches(url: string): boolean
  findContentUnits(): HTMLElement[]
  extract(el: HTMLElement): ScrapedContent
}

// djb2 — fast, deterministic, good enough for content_id during scaffold.
// TODO (Phase 1): upgrade to SHA-256 via crypto.subtle.digest if collision rate matters.
function simpleHash(s: string): string {
  let h = 5381
  for (let i = 0; i < s.length; i++) {
    h = (h << 5) + h + s.charCodeAt(i)
  }
  return (h >>> 0).toString(16).padStart(8, '0')
}

const mockSitePlugin: SitePlugin = {
  matches: (url) => url.startsWith('http://localhost:3000'),

  findContentUnits: () =>
    Array.from(document.querySelectorAll<HTMLElement>('[data-freewall-post]')),

  extract: (el) => {
    const text = el.querySelector('[data-freewall-text]')?.textContent?.trim() ?? ''
    const author = el.querySelector('[data-freewall-author]')?.textContent?.trim() ?? null
    const media_urls = Array.from(
      el.querySelectorAll<HTMLImageElement>('[data-freewall-media] img'),
    )
      .map((img) => img.src)
      .filter((src): src is string => Boolean(src))

    return {
      content_id: simpleHash(`${author ?? ''}|${text.slice(0, 256)}`),
      text,
      author,
      media_urls,
      source_url: window.location.href,
      scraped_at: new Date().toISOString(),
    }
  },
}

const PLUGINS: SitePlugin[] = [mockSitePlugin]

export function pickPlugin(url: string = window.location.href): SitePlugin | null {
  return PLUGINS.find((p) => p.matches(url)) ?? null
}
