import DemoScenarios from '@/components/DemoScenarios';
import AgentRegistry from '@/components/AgentRegistry';
import CapabilityRegistry from '@/components/CapabilityRegistry';
import MissionCompiler from '@/components/MissionCompiler';
import GovernanceDecisionPanel from '@/components/GovernanceDecisionPanel';
import SafetyNotice from '@/components/SafetyNotice';
import BackendStatus from '@/components/BackendStatus';

export default function Home() {
  return (
    <>
      <BackendStatus />
      <DemoScenarios />
      <AgentRegistry />
      <CapabilityRegistry />
      <MissionCompiler />
      <GovernanceDecisionPanel />
      <SafetyNotice />
    </>
  );
}