export default function Button({ children, onClick, variant = "primary", ...props }) {
  const base = "inline-flex items-center justify-center rounded-full px-5 h-12 text-base font-medium transition-colors";
  const variants = {
    primary: "bg-black text-white hover:bg-zinc-800 dark:bg-white dark:text-black dark:hover:bg-zinc-200",
    secondary: "border border-black/10 text-black hover:bg-black/5 dark:border-white/15 dark:text-white dark:hover:bg-white/10",
  };

  return (
    <button className={`${base} ${variants[variant]}`} onClick={onClick} {...props}>
      {children}
    </button>
  );
}
