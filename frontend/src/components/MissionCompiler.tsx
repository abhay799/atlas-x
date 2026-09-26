'use client';

import { useState } from 'react';
import { AtlasApiClient } from '@/lib/api';
import { Mission } from '@/types';

export default function MissionCompiler() {
  const [loading, setLoading] = useState(false);
  const [mission, setMission] = useState<Mission | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [objective, setObjective] = useState('');
  const [constraints, setConstraints] = useState<string[]>([]);
  

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setMission(null);
    const api = new AtlasApiClient();
    try {
      const compiledMission = await api.compileMission(objective, constraints);
      setMission(compiledMission);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="mb-8">
      <h2 className="text-2xl font-semibold mb-4">Mission Compiler</h2>
      <div className="p-4 bg-gray-800/50 rounded-lg border border-gray-700">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">
              Mission Objective
            </label>
            <textarea
              value={objective}
              onChange={(e) => setObjective(e.target.value)}
              rows={3}
              required
              minLength={5}
              className="w-full px-3 py-2 bg-gray-700/50 rounded border border-gray-600 text-white"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">
              Constraints (one per line)
            </label>
            <textarea
              value={constraints.join('\n')}
              onChange={(e) => setConstraints(e.target.value.split('\n').map((s) => s.trim()).filter(Boolean))}
              rows={3}
              className="w-full px-3 py-2 bg-gray-700/50 rounded border border-gray-600 text-white"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className={`w-full px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            {loading ? 'Compiling...' : 'Compile Mission'}
          </button>
        </form>
        {error && (
          <div className="mt-3 p-3 bg-red-900/50 rounded border border-red-500">
            <p className="text-sm text-red-400">Error: {error}</p>
          </div>
        )}
        {mission && (
          <div className="mt-4 p-3 bg-gray-900/50 rounded border border-gray-700">
            <h3 className="text-lg font-medium mb-2">Compiled Mission</h3>
            <p className="text-xs text-gray-300">Mission ID: {mission.mission_id}</p>
            <p className="text-xs text-gray-300">Objective: {mission.objective}</p>
            <p className="text-xs text-gray-300">Constraints: {mission.constraints.join(', ') || 'None'}</p>
            <p className="text-xs text-gray-300">Tasks: {mission.tasks.length}</p>
            {mission.tasks.length > 0 && (
              <div className="mt-2">
                <h4 className="text-sm font-medium mb-1">Tasks:</h4>
                <ul className="list-disc list-inside text-xs text-gray-300 space-y-1">
                  {mission.tasks.map((task) => (
                    <li key={task.task_id}>
                      <strong>{task.title}</strong> (ID: {task.task_id}) -
                      {task.dependencies.length > 0 ? `Depends on: ${task.dependencies.join(', ')}` : 'No dependencies'}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </section>
  );
}