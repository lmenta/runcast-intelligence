interface Props {
  answer: string
  query: string
}

function renderMarkdown(text: string) {
  return text
    .split('\n')
    .map((line, i) => {
      if (line.startsWith('**') && line.endsWith('**')) {
        return <p key={i} className="font-semibold text-gray-900 mt-3 mb-1">{line.slice(2, -2)}</p>
      }
      if (line.startsWith('- ')) {
        return <li key={i} className="ml-4 list-disc">{renderInline(line.slice(2))}</li>
      }
      if (line.trim() === '') return <br key={i} />
      return <p key={i} className="mb-1">{renderInline(line)}</p>
    })
}

function renderInline(text: string) {
  const parts = text.split(/(\*\*[^*]+\*\*)/g)
  return parts.map((p, i) =>
    p.startsWith('**') && p.endsWith('**')
      ? <strong key={i} className="font-semibold text-gray-900">{p.slice(2, -2)}</strong>
      : p
  )
}

export default function AnswerCard({ answer, query }: Props) {
  return (
    <div className="rounded-2xl border border-orange-100 bg-orange-50 p-6">
      <p className="mb-3 text-xs text-gray-400">Based on podcast transcripts matching "{query}"</p>
      <div className="text-[15px] leading-relaxed text-gray-700">
        {renderMarkdown(answer)}
      </div>
    </div>
  )
}
