import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const MarkdownChat = ({ children }) => {
  return (
    <div className="markdown-content max-w-none">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          // 제목들 - 채팅에 맞게 크기 조정
          h1: ({ children }) => (
            <h1 className="text-2xl font-bold mb-4 mt-6 text-gray-900 border-b border-gray-200 pb-2">
              {children}
            </h1>
          ),
          h2: ({ children }) => (
            <h2 className="text-xl font-semibold mb-3 mt-5 text-gray-800">
              {children}
            </h2>
          ),
          h3: ({ children }) => (
            <h3 className="text-lg font-medium mb-2 mt-4 text-gray-800">
              {children}
            </h3>
          ),

          // 단락 - 줄 간격 최적화
          p: ({ children }) => (
            <p className="mb-3 leading-7 text-gray-700 last:mb-0">{children}</p>
          ),

          // 리스트 - 영화 목록에 최적화
          ul: ({ children }) => (
            <ul className="list-none mb-4 space-y-2 text-gray-700">
              {children}
            </ul>
          ),
          ol: ({ children }) => (
            <ol className="list-decimal list-inside mb-4 space-y-2 text-gray-700 pl-2">
              {children}
            </ol>
          ),
          li: ({ children }) => (
            <li className="flex items-start">
              <span className="text-gray-600 mr-2 mt-1 font-medium">•</span>
              <span className="flex-1">{children}</span>
            </li>
          ),

          // 인용구 - 영화 명대사나 중요 정보용
          blockquote: ({ children }) => (
            <blockquote className="border-l-4 border-gray-400 pl-4 py-3 my-4 bg-gray-50 rounded-r-md">
              <div className="text-gray-700 italic">{children}</div>
            </blockquote>
          ),

          // 강조 텍스트 - 영화 제목용
          strong: ({ children }) => (
            <strong className="font-semibold text-gray-900  px-1 rounded">
              {children}
            </strong>
          ),

          // 기울임 - 감독, 배우명용
          em: ({ children }) => (
            <em className="italic text-gray-800 font-medium">{children}</em>
          ),

          // 링크 - 외부 링크 스타일링
          a: ({ href, children }) => (
            <a
              href={href}
              className="text-gray-800 hover:text-black hover:bg-gray-100 px-1 py-0.5 rounded transition-colors duration-200 underline decoration-2 underline-offset-2"
              target="_blank"
              rel="noopener noreferrer"
            >
              {children}
            </a>
          ),

          // 테이블 - 영화 정보 비교용
          table: ({ children }) => (
            <div className="overflow-x-auto mb-5 rounded-lg border border-gray-200 shadow-sm">
              <table className="min-w-full divide-y divide-gray-200">
                {children}
              </table>
            </div>
          ),
          thead: ({ children }) => (
            <thead className="bg-gray-50">{children}</thead>
          ),
          tbody: ({ children }) => (
            <tbody className="bg-white divide-y divide-gray-200">
              {children}
            </tbody>
          ),
          th: ({ children }) => (
            <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 tracking-wider">
              {children}
            </th>
          ),
          td: ({ children }) => (
            <td className="px-4 py-3 text-sm text-gray-700 whitespace-nowrap">
              {children}
            </td>
          ),

          // 가로선
          hr: () => <hr className="my-6 border-gray-300" />,

          // 인라인 코드 (영화 ID나 특수 표기용)
          code: ({ children }) => (
            <code className="bg-gray-100 text-gray-800 px-2 py-1 rounded text-sm font-mono">
              {children}
            </code>
          ),
        }}
      >
        {children}
      </ReactMarkdown>
    </div>
  );
};

export default MarkdownChat;
