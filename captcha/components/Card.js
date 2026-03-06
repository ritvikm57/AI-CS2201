export default function Card({ children, title, className = "" }) {
  return (
    <div className={`rounded-2xl border border-black/10 bg-white p-6 dark:border-white/10 dark:bg-zinc-900 ${className}`}>
      {title && <h3 className="mb-3 text-lg font-semibold text-black dark:text-white">{title}</h3>}
      {children}
    </div>
  );
}
