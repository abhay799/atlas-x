import {
  AtlasApiClient,
  resolveApiUrl,
} from './api';

describe('resolveApiUrl', () => {
  it('uses the configured API URL', () => {
    expect(
      resolveApiUrl(
        'https://atlas.example.com',
        'production',
      ),
    ).toBe('https://atlas.example.com');
  });

  it('removes trailing slashes', () => {
    expect(
      resolveApiUrl(
        'https://atlas.example.com/',
        'production',
      ),
    ).toBe('https://atlas.example.com');
  });

  it('throws when production URL is missing', () => {
    expect(() =>
      resolveApiUrl(undefined, 'production'),
    ).toThrow(
      'NEXT_PUBLIC_ATLAS_API_URL must be set in production',
    );
  });

  it('uses localhost during development', () => {
    expect(
      resolveApiUrl(undefined, 'development'),
    ).toBe('http://localhost:8000');
  });

  it('uses localhost during tests', () => {
    expect(
      resolveApiUrl(undefined, 'test'),
    ).toBe('http://localhost:8000');
  });
});

describe('AtlasApiClient', () => {
  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('calls the health endpoint', async () => {
    const fetchMock = jest
      .spyOn(global, 'fetch')
      .mockResolvedValue({
        ok: true,
        status: 200,
        statusText: 'OK',
        json: async () => ({
          status: 'ok',
        }),
      } as Response);

    const api = new AtlasApiClient(
      'http://localhost:8000',
    );

    const result = await api.health();

    expect(result).toEqual({
      status: 'ok',
    });

    expect(fetchMock).toHaveBeenCalledWith(
      'http://localhost:8000/health',
      expect.objectContaining({
        headers: expect.objectContaining({
          'Content-Type':
            'application/json',
        }),
      }),
    );
  });

  it('calls the readiness endpoint', async () => {
    jest
      .spyOn(global, 'fetch')
      .mockResolvedValue({
        ok: true,
        status: 200,
        statusText: 'OK',
        json: async () => ({
          status: 'ready',
          constitution_version: '2026.1',
        }),
      } as Response);

    const api = new AtlasApiClient(
      'http://localhost:8000',
    );

    const result = await api.ready();

    expect(result).toEqual({
      status: 'ready',
      constitution_version: '2026.1',
    });
  });

  it('throws when the backend returns an error', async () => {
    jest
      .spyOn(global, 'fetch')
      .mockResolvedValue({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: async () => ({
          detail: 'Backend unavailable',
        }),
      } as Response);

    const api = new AtlasApiClient(
      'http://localhost:8000',
    );

    await expect(api.health()).rejects.toThrow(
      'Backend unavailable',
    );
  });
});