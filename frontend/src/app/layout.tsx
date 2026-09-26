import './globals.css';
import { Inter } from 'next/font/google';
import Head from '@/components/Head';
import Header from '@/components/Header';
import BackendStatus from '@/components/BackendStatus';
import DemoScenarios from '@/components/DemoScenarios';
import AgentRegistry from '@/components/AgentRegistry';
import CapabilityRegistry from '@/components/CapabilityRegistry';
import MissionCompiler from '@/components/MissionCompiler';
import GovernanceDecisionPanel from '@/components/GovernanceDecisionPanel';
import SafetyNotice from '@/components/SafetyNotice';

const inter = Inter({ subsets: ['latin'] });

export const metadata = {
  title: 'ATLAS X Mission Control',
  description: 'Public demo of ATLAS X governance workflows',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={inter.className}>
      <Head />
      <body className="bg-gray-900 text-gray-100 min-h-screen">
        <Header />
        <main className="container mx-auto px-4 py-8">
          <BackendStatus />
          <DemoScenarios />
          <AgentRegistry />
          <CapabilityRegistry />
          <MissionCompiler />
          <GovernanceDecisionPanel />
          <SafetyNotice />
        </main>
        {children}
      </body>
    </html>
  );
}