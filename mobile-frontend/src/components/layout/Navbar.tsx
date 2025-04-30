
'use client';

import { Fragment, useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Disclosure, Menu as HeadlessMenu, Transition } from '@headlessui/react'; // Renamed Menu to HeadlessMenu to avoid conflict
import { Menu as MenuIcon, X, Bell, Wallet, UserCircle } from 'lucide-react'; // Use Lucide icons, import Menu as MenuIcon
import { Button } from '@/components/ui/button'; // Import shadcn Button
import { cn } from '@/lib/utils'; // Utility for class names

const navigation = [
  { name: 'Dashboard', href: '/dashboard' },
  { name: 'Portfolio', href: '/portfolio' },
  { name: 'Market Analysis', href: '/market-analysis' },
  { name: 'Recommendations', href: '/recommendations' },
  { name: 'Blockchain Explorer', href: '/blockchain-explorer' },
];

export default function Navbar() {
  const pathname = usePathname();
  const [walletConnected, setWalletConnected] = useState(false);
  const [walletAddress, setWalletAddress] = useState('');

  const connectWallet = async () => {
    // Placeholder for actual wallet connection logic
    setWalletConnected(true);
    setWalletAddress('0x1234...5678');
  };

  const disconnectWallet = () => {
    setWalletConnected(false);
    setWalletAddress('');
  };

  return (
    // Updated background and border color for consistency
    <Disclosure as="nav" className="bg-zinc-950 border-b border-zinc-800 sticky top-0 z-40">
      {({ open }) => (
        <>
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="flex h-16 justify-between">
              <div className="flex items-center">
                {/* Mobile menu button (visible on small screens) */}
                <div className="-ml-2 mr-2 flex items-center md:hidden">
                  <Disclosure.Button className="inline-flex items-center justify-center rounded-md p-2 text-zinc-400 hover:bg-zinc-800 hover:text-white focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white">
                    <span className="sr-only">Open main menu</span>
                    {open ? (
                      <X className="block h-6 w-6" aria-hidden="true" /> // Use Lucide X
                    ) : (
                      <MenuIcon className="block h-6 w-6" aria-hidden="true" /> // Use Lucide MenuIcon
                    )}
                  </Disclosure.Button>
                </div>
                {/* Logo */}
                <div className="flex flex-shrink-0 items-center">
                  <Link href="/" className="flex items-center">
                    {/* Consider adding a logo image here */}
                    <span className="text-white font-bold text-xl">QuantumNest</span>
                  </Link>
                </div>
                {/* Desktop Navigation Links (hidden on small screens) */}
                <div className="hidden md:ml-6 md:flex md:space-x-4">
                  {navigation.map((item) => (
                    <Link
                      key={item.name}
                      href={item.href}
                      className={cn(
                        pathname === item.href
                          ? 'border-indigo-500 text-white'
                          : 'border-transparent text-zinc-400 hover:border-zinc-700 hover:text-white',
                        'inline-flex items-center border-b-2 px-1 pt-1 text-sm font-medium'
                      )}
                      aria-current={pathname === item.href ? 'page' : undefined}
                    >
                      {item.name}
                    </Link>
                  ))}
                </div>
              </div>

              {/* Right side actions (Wallet, Notifications, Profile) */}
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  {!walletConnected ? (
                    <Button variant="outline" size="sm" onClick={connectWallet} className="text-white border-indigo-600 hover:bg-indigo-700 hover:text-white">
                      <Wallet className="mr-2 h-4 w-4" /> Connect Wallet
                    </Button>
                  ) : (
                    <div className="flex items-center space-x-3">
                      <span className="text-zinc-400 text-sm hidden sm:block">{walletAddress}</span>
                      <Button variant="ghost" size="icon" className="text-zinc-400 hover:text-white hover:bg-zinc-800">
                        <span className="sr-only">View notifications</span>
                        <Bell className="h-5 w-5" />
                      </Button>

                      {/* Profile dropdown */}
                      <HeadlessMenu as="div" className="relative"> {/* Use HeadlessMenu */}
                        <HeadlessMenu.Button as={Button} variant="ghost" size="icon" className="rounded-full text-zinc-400 hover:text-white hover:bg-zinc-800">
                          <span className="sr-only">Open user menu</span>
                          <UserCircle className="h-6 w-6" />
                        </HeadlessMenu.Button>
                        <Transition
                          as={Fragment}
                          enter="transition ease-out duration-100"
                          enterFrom="transform opacity-0 scale-95"
                          enterTo="transform opacity-100 scale-100"
                          leave="transition ease-in duration-75"
                          leaveFrom="transform opacity-100 scale-100"
                          leaveTo="transform opacity-0 scale-95"
                        >
                          <HeadlessMenu.Items className="absolute right-0 z-10 mt-2 w-48 origin-top-right rounded-md bg-zinc-900 py-1 shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none border border-zinc-800">
                            <HeadlessMenu.Item>
                              {({ active }) => (
                                <Link
                                  href="/profile"
                                  className={cn(active ? 'bg-zinc-800' : '', 'block px-4 py-2 text-sm text-zinc-200')}
                                >
                                  Your Profile
                                </Link>
                              )}
                            </HeadlessMenu.Item>
                            <HeadlessMenu.Item>
                              {({ active }) => (
                                <Link
                                  href="/settings"
                                  className={cn(active ? 'bg-zinc-800' : '', 'block px-4 py-2 text-sm text-zinc-200')}
                                >
                                  Settings
                                </Link>
                              )}
                            </HeadlessMenu.Item>
                            <HeadlessMenu.Item>
                              {({ active }) => (
                                <button
                                  onClick={disconnectWallet}
                                  className={cn(active ? 'bg-zinc-800' : '', 'block w-full text-left px-4 py-2 text-sm text-red-400')}
                                >
                                  Disconnect
                                </button>
                              )}
                            </HeadlessMenu.Item>
                          </HeadlessMenu.Items>
                        </Transition>
                      </HeadlessMenu>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Mobile Menu Panel (shown when mobile menu button is clicked) */}
          <Disclosure.Panel className="md:hidden border-t border-zinc-800">
            <div className="space-y-1 px-2 pb-3 pt-2">
              {navigation.map((item) => (
                <Disclosure.Button
                  key={item.name}
                  as={Link} // Use Link for navigation
                  href={item.href}
                  className={cn(
                    pathname === item.href
                      ? 'bg-zinc-800 text-white'
                      : 'text-zinc-400 hover:bg-zinc-700 hover:text-white',
                    'block rounded-md px-3 py-2 text-base font-medium'
                  )}
                  aria-current={pathname === item.href ? 'page' : undefined}
                >
                  {item.name}
                </Disclosure.Button>
              ))}
            </div>
            {/* Wallet info/actions in mobile menu */}
            {walletConnected && (
              <div className="border-t border-zinc-700 pb-3 pt-4">
                <div className="flex items-center px-5">
                  <div className="flex-shrink-0">
                    <UserCircle className="h-10 w-10 rounded-full text-zinc-400" />
                  </div>
                  <div className="ml-3">
                    <div className="text-base font-medium text-white">User</div>
                    <div className="text-sm font-medium text-zinc-400 truncate w-48">{walletAddress}</div>
                  </div>
                  <Button variant="ghost" size="icon" className="ml-auto flex-shrink-0 rounded-full text-zinc-400 hover:text-white hover:bg-zinc-800">
                    <span className="sr-only">View notifications</span>
                    <Bell className="h-6 w-6" />
                  </Button>
                </div>
                <div className="mt-3 space-y-1 px-2">
                  <Disclosure.Button
                    as={Link}
                    href="/profile"
                    className="block rounded-md px-3 py-2 text-base font-medium text-zinc-400 hover:bg-zinc-700 hover:text-white"
                  >
                    Your Profile
                  </Disclosure.Button>
                  <Disclosure.Button
                    as={Link}
                    href="/settings"
                    className="block rounded-md px-3 py-2 text-base font-medium text-zinc-400 hover:bg-zinc-700 hover:text-white"
                  >
                    Settings
                  </Disclosure.Button>
                  <Disclosure.Button
                    as="button"
                    onClick={disconnectWallet}
                    className="block w-full text-left rounded-md px-3 py-2 text-base font-medium text-red-400 hover:bg-zinc-700 hover:text-white"
                  >
                    Disconnect
                  </Disclosure.Button>
                </div>
              </div>
            )}
          </Disclosure.Panel>
        </>
      )}
    </Disclosure>
  );
}

