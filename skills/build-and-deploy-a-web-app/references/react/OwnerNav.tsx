'use client';

import { useEffect, useState } from 'react';
import { useUser } from '@/lib/user-context';

/**
 * Owner-only navigation bar. The owner's id lives server-side only, so instead
 * of comparing ids we ask the backend whether we're the owner (re-checking
 * whenever auth state changes). Render it inside <UserProvider> in app/layout.tsx,
 * before the main content.
 */
export default function OwnerNav() {
  const { authenticated } = useUser();
  const [isOwner, setIsOwner] = useState(false);

  useEffect(() => {
    if (!authenticated) {
      setIsOwner(false);
      return;
    }
    let cancelled = false;
    (async () => {
      try {
        const res = await fetch('/api/harness/owner');
        const ok = res.ok && (await res.json()).isOwner === true;
        if (!cancelled) setIsOwner(ok);
      } catch {
        if (!cancelled) setIsOwner(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [authenticated]);

  if (!isOwner) return null;

  return (
    <nav className="sticky top-0 z-50 bg-fulcra-black/50 border-b border-fulcra-gray/20">
      <div className="max-w-7xl mx-auto px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <a href="/" className="text-fulcra-teal hover:text-fulcra-teal/80 font-medium">
              Home
            </a>
            <a href="/harness" className="text-fulcra-teal hover:text-fulcra-teal/80 font-medium">
              Harness Dashboard
            </a>
          </div>
          <div className="text-fulcra-gray text-sm">Owner</div>
        </div>
      </div>
    </nav>
  );
}
