/**
 * Markdown renderer for tutor messages.
 *
 * Uses react-markdown + remark-gfm, so bold/italic, lists, blockquotes,
 * headings, code and GFM tables all render correctly.
 *
 * Tutor skills also emit two non-standard constructs, normalised before
 * rendering:
 *   □ I can …   (success criteria, set-success-criteria skill)
 *   ☑ I can …   (ticked criterion)
 * These become GFM task-list items so they display as checkbox lists.
 *
 * Raw HTML in tutor text is NOT rendered (react-markdown default) — safe
 * against injection without a sanitiser.
 */

import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import remarkBreaks from 'remark-breaks'

/**
 * Convert the skills' checkbox-style bullets into GFM task lists and
 * normalise other common bullet characters the model may emit.
 */
function normalizeTutorMarkdown(src: string): string {
  const lines = src.split('\n')
  const out: string[] = []

  for (const line of lines) {
    // "□ I can …" / "☐ I can …" (optionally indented, optionally after - / * / •)
    const unchecked = line.match(/^\s*(?:[-*•]\s+)?[□☐]\s+(.*)$/)
    // "☑ I can …" / "✔ …" (already ticked)
    const checked = line.match(/^\s*(?:[-*•]\s+)?[☑✔✓]\s+(.*)$/)
    const converted = unchecked
      ? `- [ ] ${unchecked[1]}`
      : checked
        ? `- [x] ${checked[1]}`
        : null

    // A plain line directly after a converted checkbox item would be
    // absorbed into the last <li> — separate it with a blank line.
    const prevWasItem = out.length > 0 && out[out.length - 1].startsWith('- [')
    if (!converted && prevWasItem && line.trim() !== '') out.push('')

    out.push(converted ?? line)
  }

  return out.join('\n')
}

interface MarkdownProps {
  text: string
  className?: string
}

export default function Markdown({ text, className = '' }: MarkdownProps) {
  return (
    <div className={className}>
      <ReactMarkdown remarkPlugins={[remarkGfm, remarkBreaks]}>
        {normalizeTutorMarkdown(text)}
      </ReactMarkdown>
    </div>
  )
}
