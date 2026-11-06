"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { Brand } from "@/components/ui/brand";
import { navigation } from "@/lib/navigation";

export function AppSidebar() {
  const pathname = usePathname();

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <Brand />
      </div>

      <nav className="sidebar-nav" aria-label="Navegação principal">
        {navigation.map((section) => (
          <div className="nav-section" key={section.title}>
            <p className="nav-section-title">{section.title}</p>
            <ul className="nav-list">
              {section.items.map((item) => {
                const isActive = item.href !== undefined && pathname === item.href;
                if (item.href) {
                  return (
                    <li key={item.key}>
                      <Link
                        className={`nav-link${isActive ? " nav-link--active" : ""}`}
                        href={item.href}
                      >
                        <span>{item.label}</span>
                      </Link>
                    </li>
                  );
                }
                return (
                  <li key={item.key}>
                    <span className="nav-link nav-link--disabled">
                      <span>{item.label}</span>
                      <span className="nav-phase">F{item.phase}</span>
                    </span>
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </nav>

      <div className="sidebar-footer">
        <span className="sidebar-footer-label">Fundação</span>
        <span className="sidebar-footer-value">FASE 1</span>
      </div>
    </aside>
  );
}
