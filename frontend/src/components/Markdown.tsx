/**
 * Lightweight Markdown renderer for tutor messages.
 *
 * Supports:
 *   *italic*  _italic_
 *   **bold**  __bold__
 *   - list item
 *   > blockquote
 *   paragraphs (blank-line separation)
 *
 * Escapes HTML to prevent injection.
 */

function escapeHtml(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
}

function inlineMarkdown(text: string): string {
  return (
    text
      // bold
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/__(.+?)__/g, '<strong>$1</strong>')
      // italic
      .replace(/\*(.+?)\*/g, '<em>$1</em>')
      .replace(/_(.+?)_/g, '<em>$1</em>')
  )
}

function blockMarkdown(src: string): string {
  const blocks: string[] = []
  const lines = src.split('\n')
  let i = 0

  while (i < lines.length) {
    const line = lines[i]

    // Blockquote
    if (line.startsWith('> ')) {
      const quoteLines: string[] = []
      while (i < lines.length && lines[i].startsWith('> ')) {
        quoteLines.push(lines[i].slice(2))
        i++
      }
      const content = inlineMarkdown(escapeHtml(quoteLines.join('\n')))
        .split('\n')
        .join('<br>')
      blocks.push(`<blockquote class="tutor-quote">${content}</blockquote>`)
      continue
    }

    // Unordered list
    if (line.startsWith('- ') || line.startsWith('* ')) {
      const items: string[] = []
      while (
        i < lines.length &&
        (lines[i].startsWith('- ') || lines[i].startsWith('* '))
      ) {
        items.push(lines[i].slice(2))
        i++
      }
      const lis = items
        .map((item) => `<li>${inlineMarkdown(escapeHtml(item))}</li>`)
        .join('')
      blocks.push(`<ul class="tutor-list">${lis}</ul>`)
      continue
    }

    // Empty line → skip
    if (line.trim() === '') {
      i++
      continue
    }

    // Paragraph
    const paraLines: string[] = []
    while (i < lines.length && lines[i].trim() !== '') {
      paraLines.push(lines[i])
      i++
    }
    const content = inlineMarkdown(escapeHtml(paraLines.join(' ')))
    blocks.push(`<p class="tutor-para">${content}</p>`)
  }

  return blocks.join('')
}

export function renderMarkdown(src: string): string {
  return blockMarkdown(src)
}

interface MarkdownProps {
  text: string
  className?: string
}

export default function Markdown({ text, className = '' }: MarkdownProps) {
  const html = renderMarkdown(text)
  return (
    <div
      className={className}
      dangerouslySetInnerHTML={{ __html: html }}
    />
  )
}
