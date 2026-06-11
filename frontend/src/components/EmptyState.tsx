import Link from "next/link";

interface Props {
  icon?: string;
  title: string;
  description: string;
  action?: { label: string; href: string };
}

export function EmptyState({ icon = "⚽", title, description, action }: Props) {
  return (
    <div className="flex flex-col items-center rounded-xl border border-dashed border-gray-200 bg-gray-50 px-6 py-10 text-center">
      <span className="mb-3 text-4xl" aria-hidden>
        {icon}
      </span>
      <h3 className="text-lg font-semibold text-gray-800">{title}</h3>
      <p className="mt-2 max-w-sm text-sm text-gray-500">{description}</p>
      {action && (
        <Link href={action.href} className="btn-primary mt-5 text-sm">
          {action.label}
        </Link>
      )}
    </div>
  );
}
