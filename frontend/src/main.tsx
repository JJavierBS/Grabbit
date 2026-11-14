import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './styles/base.css';
import { App } from './App';
import { setTransport } from './api/client';
import { ToastProvider } from './components/Toast';
import { Gallery } from './design/Gallery';

if (import.meta.env.VITE_FAKE_API === '1') {
  const { fakeTransport } = await import('./dev/fakeApi');
  setTransport(fakeTransport);
}

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: 1, refetchOnWindowFocus: false } },
});

const root = document.getElementById('root');
if (!root) throw new Error('Missing #root element');

createRoot(root).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <ToastProvider>
        {new URLSearchParams(location.search).has('gallery') ? <Gallery /> : <App />}
      </ToastProvider>
    </QueryClientProvider>
  </StrictMode>,
);
