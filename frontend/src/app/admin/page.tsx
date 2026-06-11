"use client";

import Link from "next/link";

const SECTIONS = [
  {
    href: "/admin/matches",
    title: "Match Scores",
    description: "Enter final scores, set status to finished, and recalculate prediction points.",
    icon: "⚽",
  },
  {
    href: "/admin/tournaments",
    title: "Tournaments",
    description: "Create competitions and activate or deactivate them for users.",
    icon: "🏆",
  },
  {
    href: "/admin/stages",
    title: "Stages",
    description: "Add group stages and knockout rounds to a tournament.",
    icon: "📅",
  },
  {
    href: "/admin/cup-groups",
    title: "Cup Groups",
    description: "Create groups (A, B, C…) and assign teams.",
    icon: "👥",
  },
  {
    href: "/admin/teams",
    title: "Teams",
    description: "Add national or club teams with codes and flag URLs.",
    icon: "🌍",
  },
];

export default function AdminOverviewPage() {
  return (
    <div>
      <h1 className="mb-2 text-3xl font-bold">Admin Overview</h1>
      <p className="mb-8 text-gray-600">
        Manage tournaments, fixtures, and results without Django admin.
      </p>
      <div className="grid gap-4 sm:grid-cols-2">
        {SECTIONS.map((section) => (
          <Link key={section.href} href={section.href} className="card transition hover:border-pitch-200 hover:shadow-md">
            <div className="mb-2 text-2xl">{section.icon}</div>
            <h2 className="font-semibold text-pitch-800">{section.title}</h2>
            <p className="mt-1 text-sm text-gray-600">{section.description}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
