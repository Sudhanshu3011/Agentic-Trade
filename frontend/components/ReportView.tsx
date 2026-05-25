import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { downloadMarkdown, downloadPdf } from "@/lib/download";

export function ReportView({
  title,
  ticker,
  status,
  content,
  accent,
  filenameBase,
}: {
  title: string;
  ticker: string;
  status: string;
  content: string;
  accent?: string;
  filenameBase: string;
}) {
  return (
    <div className="mx-auto max-w-[920px]">
      <div className="mb-2 flex items-center justify-between">
        <h2 className="flex items-center gap-3 text-[18px] font-medium text-[var(--foreground)]">
          {accent && (
            <span
              className="inline-block h-2.5 w-2.5"
              style={{ background: accent }}
            />
          )}
          {title}
        </h2>
        <div className="flex items-center gap-4">
          <DownloadBtn onClick={() => downloadPdf(`${filenameBase}`, content)}>
            ↓ PDF
          </DownloadBtn>
          <DownloadBtn
            onClick={() => downloadMarkdown(filenameBase, content)}
          >
            ↓ MD
          </DownloadBtn>
        </div>
      </div>
      <div className="h-px w-full bg-[var(--border)]" />
      <p className="mt-2 font-mono text-[12px] text-[var(--muted-foreground)]">
        {ticker} · Report generated · {status}
      </p>

      <div className="mt-6 border border-[var(--border)] bg-white dark:bg-zinc-900 p-6">
        <Markdown content={content} />
      </div>
    </div>
  );
}

export function Markdown({ content }: { content: string }) {
  return (
    <div className="prose prose-sm prose-zinc max-w-none prose-headings:font-mono prose-h2:border-b prose-h2:border-[var(--border)] prose-h2:pb-1 prose-strong:text-[var(--foreground)] prose-code:bg-[var(--background)] prose-code:px-1 prose-code:py-0.5 prose-code:font-mono prose-code:text-[12px] prose-code:before:content-none prose-code:after:content-none prose-table:text-[13px] prose-th:border prose-th:border-[var(--border)] prose-th:bg-[var(--background)] prose-th:px-3 prose-th:py-2 prose-td:border prose-td:border-[var(--border)] prose-td:px-3 prose-td:py-2 prose-a:text-[var(--foreground)] prose-a:no-underline hover:prose-a:underline">
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
    </div>
  );
}

function DownloadBtn({
  onClick,
  children,
}: {
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      className="font-mono text-[12px] text-[var(--muted-foreground)] transition-colors hover:text-[var(--foreground)]"
    >
      {children}
    </button>
  );
}
