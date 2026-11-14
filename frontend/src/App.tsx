import { ToastProvider } from './components/Toast';
import { Gallery } from './design/Gallery';

export function App() {
  return (
    <ToastProvider>
      <Gallery />
    </ToastProvider>
  );
}
