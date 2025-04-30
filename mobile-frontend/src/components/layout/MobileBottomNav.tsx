
'use client';

import { useState } from 'react';
import { usePathname } from 'next/navigation';
import Link from 'next/link';
import { LayoutDashboard, Briefcase, LineChart, Sparkles } from 'lucide-react'; // Import Lucide icons

export default function MobileBottomNav() {
  const pathname = usePathname();

  // Updated navigation with Lucide icons
  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    { name: 'Portfolio', href: '/portfolio', icon: Briefcase },
    { name: 'Market', href: '/market-analysis', icon: LineChart },
    { name: 'Recommend', href: '/recommendations', icon: Sparkles },
  ];

  return (
    // Slightly improved styling: darker background, softer border
    <div className="fixed bottom-0 left-0 z-50 w-full h-16 bg-zinc-950 border-t border-zinc-800 md:hidden">
      <div className="grid h-full grid-cols-4">
        {navigation.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`inline-flex flex-col items-center justify-center px-2 sm:px-5 group ${
                isActive ? 'text-indigo-400' : 'text-zinc-400 hover:text-zinc-50'
              }`}
            >
              <Icon className="w-5 h-5 mb-1" />
              <span className="text-xs">{item.name}</span>
              {/* Optional: Add a small indicator for active state */}
              {/* {isActive && <span className="absolute bottom-1 w-1 h-1 bg-indigo-400 rounded-full"></span>} */}
            </Link>
          );
        })}
      </div>
    </div>
  );
}

