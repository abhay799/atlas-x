'use client';

import { useEffect, useState } from 'react';
import { AtlasApiClient } from '@/lib/api';
import { Capability } from '@/types';

export default function CapabilityRegistry() {
  const [loading, setLoading] = useState(false);
  const [capabilities, setCapabilities] = useState<Capability[]>([]);
  const [newCapability, setNewCapability] = useState<Omit<Capability, 'version' | 'provenance'>>({
    name: '',
    scope: 'global',
    restrictions: [],
  });

  useEffect(() => {
    // Only run in browser
    if (typeof window !== 'undefined') {
      const loadCapabilities = () => {
        try {
          const capabilitiesJson = localStorage.getItem('atlas-demo-capabilities');
          const capabilities = capabilitiesJson ? JSON.parse(capabilitiesJson) : [];
          setCapabilities(capabilities);
        } catch (e) {
          console.error('Failed to load capabilities from localStorage:', e);
          setCapabilities([]);
        }
      };
      loadCapabilities();
    }
  }, []);

  useEffect(() => {
    // Only run in browser
    if (typeof window !== 'undefined') {
      try {
        localStorage.setItem('atlas-demo-capabilities', JSON.stringify(capabilities));
      } catch (e) {
        console.error('Failed to save capabilities to localStorage:', e);
      }
    }
  }, [capabilities]);

  const handleRegisterCapability = async () => {
    setLoading(true);
    const api = new AtlasApiClient();
    try {
      const capability: Capability = {
        name: newCapability.name,
        scope: newCapability.scope,
        restrictions: newCapability.restrictions,
        version: '1.0',
        provenance: 'declared',
      };
      const registeredCap = await api.registerCapability(capability);
      setCapabilities(prev => [...prev, registeredCap]);
      // Reset form
      setNewCapability({ name: '', scope: 'global', restrictions: [] });
    } catch (error) {
      console.error('Failed to register capability:', error);
      alert('Failed to register capability: ' + (error as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="mb-8">
      <h2 className="text-2xl font-semibold mb-4">Capability Registry</h2>
      <div className="grid gap-4 md:grid-cols-2">
        <div className="p-4 bg-gray-800/50 rounded-lg border border-gray-700">
          <h3 className="text-lg font-medium mb-2">Register Capability</h3>
          <form onSubmit={(e) => {
            e.preventDefault();
            handleRegisterCapability();
          }} className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Capability Name</label>
              <input
                value={newCapability.name}
                onChange={(e) => setNewCapability({ ...newCapability, name: e.target.value })}
                type="text"
                required
                className="w-full px-3 py-2 bg-gray-700/50 rounded border border-gray-600 text-white"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Scope</label>
              <select
                value={newCapability.scope}
                onChange={(e) => setNewCapability({ ...newCapability, scope: e.target.value })}
                className="w-full px-3 py-2 bg-gray-700/50 rounded border border-gray-600 text-white"
              >
                <option value="global">global</option>
                <option value="mission">mission</option>
                <option value="agent">agent</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Restrictions (comma-separated)</label>
              <input
                value={newCapability.restrictions.join(',')}
                onChange={(e) => setNewCapability({ ...newCapability, restrictions: e.target.value.split(',').map((s) => s.trim()).filter(Boolean) })}
                type="text"
                className="w-full px-3 py-2 bg-gray-700/50 rounded border border-gray-600 text-white"
              />
            </div>
            <button type="submit" disabled={loading} className={`w-full px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}>
              {loading ? 'Registering...' : 'Register Capability'}
            </button>
          </form>
        </div>
        <div className="p-4 bg-gray-800/50 rounded-lg border border-gray-700">
          <h3 className="text-lg font-medium mb-2">Registered Capabilities</h3>
          {capabilities.length === 0 ? (
            <p className="text-gray-400">No capabilities registered yet.</p>
          ) : (
            <div className="space-y-2">
              {capabilities.map((cap) => (
                <div key={cap.name} className="p-3 bg-gray-900/50 rounded border border-gray-700">
                  <p className="font-medium text-white">Capability: {cap.name}</p>
                  <p className="text-sm text-gray-300">Scope: {cap.scope}</p>
                  {cap.restrictions.length > 0 && (
                    <p className="text-sm text-gray-300">Restrictions: {cap.restrictions.join(', ')}</p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </section>
  );
}