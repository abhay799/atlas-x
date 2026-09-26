import AgentRegistry from '@/components/AgentRegistry';
import BackendStatus from '@/components/BackendStatus';
import CapabilityRegistry from '@/components/CapabilityRegistry';
import DemoScenarios from '@/components/DemoScenarios';
import GovernanceDecisionPanel from '@/components/GovernanceDecisionPanel';
import Header from '@/components/Header';
import MissionCompiler from '@/components/MissionCompiler';
import SafetyNotice from '@/components/SafetyNotice';

export default function Home() {
  return (
    <main className="atlas-shell">
      <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        <Header />

        <section className="mb-6">
          <div className="atlas-panel atlas-panel-accent overflow-hidden p-6 sm:p-8">
            <div className="grid gap-8 lg:grid-cols-[1.6fr_1fr] lg:items-center">
              <div>
                <p className="atlas-eyebrow mb-3">
                  Autonomous AI Governance
                </p>

                <h1 className="max-w-4xl text-4xl font-semibold tracking-tight text-white sm:text-5xl">
                  ATLAS X Mission Control
                </h1>

                <p className="mt-4 max-w-3xl text-base leading-7 text-slate-300 sm:text-lg">
                  Governance, authority, policy evaluation, mission compilation,
                  and human oversight for autonomous AI systems.
                </p>

                <div className="mt-6 flex flex-wrap gap-3 text-sm">
                  <span className="rounded-full border border-cyan-400/20 bg-cyan-400/5 px-3 py-1.5 text-cyan-200">
                    Governance Gateway
                  </span>

                  <span className="rounded-full border border-blue-400/20 bg-blue-400/5 px-3 py-1.5 text-blue-200">
                    Policy Engine
                  </span>

                  <span className="rounded-full border border-emerald-400/20 bg-emerald-400/5 px-3 py-1.5 text-emerald-200">
                    Human Authority Final
                  </span>
                </div>
              </div>

              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-1">
                <div className="rounded-2xl border border-slate-700/60 bg-slate-950/40 p-4">
                  <p className="text-xs uppercase tracking-[0.18em] text-slate-500">
                    Governance Principle
                  </p>

                  <p className="mt-2 text-lg font-medium text-white">
                    No agent receives unlimited authority.
                  </p>
                </div>

                <div className="rounded-2xl border border-slate-700/60 bg-slate-950/40 p-4">
                  <p className="text-xs uppercase tracking-[0.18em] text-slate-500">
                    Decision Outcomes
                  </p>

                  <div className="mt-3 flex flex-wrap gap-2 text-xs font-semibold">
                    <span className="rounded-full border border-emerald-400/25 bg-emerald-400/10 px-2.5 py-1 text-emerald-300">
                      ALLOW
                    </span>

                    <span className="rounded-full border border-amber-400/25 bg-amber-400/10 px-2.5 py-1 text-amber-300">
                      HUMAN APPROVAL
                    </span>

                    <span className="rounded-full border border-rose-400/25 bg-rose-400/10 px-2.5 py-1 text-rose-300">
                      BLOCK
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="mb-6">
          <div className="atlas-panel p-5">
            <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
              <div>
                <p className="atlas-eyebrow">
                  Control Plane
                </p>

                <h2 className="mt-1 text-xl font-semibold text-white">
                  System Status
                </h2>
              </div>

              <div className="flex items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-400/5 px-3 py-1.5 text-xs font-medium text-emerald-300">
                <span className="atlas-status-dot" />
                Live governance environment
              </div>
            </div>

            <BackendStatus />
          </div>
        </section>

        <section className="mb-6 grid gap-6 lg:grid-cols-2">
          <div className="atlas-panel p-5">
            <div className="mb-4">
              <p className="atlas-eyebrow">
                Identity & Authority
              </p>

              <h2 className="mt-1 text-xl font-semibold text-white">
                Agent Registry
              </h2>

              <p className="mt-2 text-sm text-slate-400">
                Register agents, assign authority levels, and maintain traceable
                identities.
              </p>
            </div>

            <AgentRegistry />
          </div>

          <div className="atlas-panel p-5">
            <div className="mb-4">
              <p className="atlas-eyebrow">
                Capability Control
              </p>

              <h2 className="mt-1 text-xl font-semibold text-white">
                Capability Registry
              </h2>

              <p className="mt-2 text-sm text-slate-400">
                Declare capabilities and scopes before autonomous systems may
                act.
              </p>
            </div>

            <CapabilityRegistry />
          </div>
        </section>

        <section className="mb-6">
          <div className="atlas-panel atlas-panel-accent p-5 sm:p-6">
            <div className="mb-5">
              <p className="atlas-eyebrow">
                Mission Planning
              </p>

              <h2 className="mt-1 text-2xl font-semibold text-white">
                Mission Compiler
              </h2>

              <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">
                Convert high-level objectives into governed mission structures
                with constraints, authority limits, and traceable tasks.
              </p>
            </div>

            <MissionCompiler />
          </div>
        </section>

        <section className="mb-6">
          <div className="atlas-panel p-5 sm:p-6">
            <div className="mb-5 flex flex-wrap items-end justify-between gap-3">
              <div>
                <p className="atlas-eyebrow">
                  Governance Gateway
                </p>

                <h2 className="mt-1 text-2xl font-semibold text-white">
                  Decision Center
                </h2>

                <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">
                  Evaluate mission tasks against authority, policy, and
                  governance constraints.
                </p>
              </div>

              <div className="grid grid-cols-3 gap-2 text-center text-[11px] font-semibold">
                <div className="rounded-lg border border-emerald-400/20 bg-emerald-400/5 px-3 py-2 text-emerald-300">
                  ALLOW
                </div>

                <div className="rounded-lg border border-amber-400/20 bg-amber-400/5 px-3 py-2 text-amber-300">
                  APPROVAL
                </div>

                <div className="rounded-lg border border-rose-400/20 bg-rose-400/5 px-3 py-2 text-rose-300">
                  BLOCK
                </div>
              </div>
            </div>

            <GovernanceDecisionPanel />
          </div>
        </section>

        <section className="mb-6">
          <div className="atlas-panel p-5 sm:p-6">
            <div className="mb-5">
              <p className="atlas-eyebrow">
                Scenario Lab
              </p>

              <h2 className="mt-1 text-2xl font-semibold text-white">
                Governance Scenarios
              </h2>

              <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">
                Run deterministic demonstrations of low-risk, human-review, and
                policy-blocked actions.
              </p>
            </div>

            <DemoScenarios />
          </div>
        </section>

        <section className="mb-10">
          <div className="atlas-panel border-amber-400/15 p-5 sm:p-6">
            <div className="mb-4">
              <p className="atlas-eyebrow">
                Human Control
              </p>

              <h2 className="mt-1 text-xl font-semibold text-white">
                Safety Boundary
              </h2>
            </div>

            <SafetyNotice />
          </div>
        </section>

        <footer className="border-t border-slate-800/70 py-6 text-center text-xs text-slate-600">
          ATLAS X · Autonomous AI Governance & Mission Control
        </footer>
      </div>
    </main>
  );
}