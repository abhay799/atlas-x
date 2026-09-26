import Link from 'next/link';

export default function Head() {
  return (
    <header className="bg-gray-800/50 backdrop-blur-sm">
      <div className="container mx-auto px-4 flex h-16 items-center justify-between">
        <Link href="/" className="flex items-center space-x-3">
          <span className="text-2xl font-bold text-blue-400">ATLAS X</span>
          <span className="text-sm text-gray-400">Mission Control</span>
        </Link>
        <nav className="hidden md:flex space-x-6 text-sm text-gray-400">
          <Link href="#" className="hover:text-white transition-colors">Docs</Link>
          <Link href="#" className="hover:text-white transition-colors">API</Link>
          <Link href="#" className="hover:text-white transition-colors">GitHub</Link>
        </nav>
      </div>
    </header>
  );
}