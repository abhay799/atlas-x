'use client';

import { useEffect, useState } from 'react';
import { AtlasApiClient } from '@/lib/api';

export default function BackendStatus() {
  const [status, setStatus] = useState<{ apiOnline: boolean; constitutionVersion?: string }>({
    apiOnline: false,
  });

  useEffect(() => {
    const checkBackend = async () => {
      const api = new AtlasApiClient();
      try {
        const health = await api.health();
        const ready = await api.ready();
        setStatus({
          apiOnline: health.status === 'ok',
          constitutionVersion: ready.constitution_version,
        });
      } catch (error) {
        console.error('Backend check failed:', error);
        setStatus({ apiOnline: false });
      }
    };

    checkBackend();
    const interval = setInterval(checkBackend, 5000); // Check every 5 seconds
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="mb-6 p-4 bg-gray-800/50 rounded-lg border border-gray-700">
      <h2 className="text-lg font-semibold mb-2">Backend Status</h2>
      <div className="flex flex-col space-y-2">
        <div className="flex items-center">
          <span className="w-3 h-3 rounded-full">
            {status.apiOnline ? (
              <span className="bg-green-500" aria-label="Online"></span>
            ) : (
              <span className="bg-red-500" aria-label="Offline"></span>
            )}
          </span>
          <span className="ml-2">
            API: {status.apiOnline ? 'Online' : 'Offline'}
          </span>
        </div>
        {status.constitutionVersion && (
          <div className="flex items-center text-sm text-gray-400">
            <span className="w-3 h-3 rounded-full bg-blue-500" aria-label="Constitution loaded"></span>
            <span className="ml-2">Constitution version: {status.constitutionVersion}</span>
          </div>
        )}
      </div>
    </div>
  );
}