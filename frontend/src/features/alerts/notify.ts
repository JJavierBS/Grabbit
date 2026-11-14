import type { Alert } from '../../api/types';

export const SIMULATED_LABEL = 'Simulated event';

const supported = () => typeof window !== 'undefined' && 'Notification' in window;

/** Asks once, when the first report is confirmed (flow.md 2). Never throws. */
export async function askNotificationPermission(): Promise<NotificationPermission | 'unsupported'> {
  if (!supported()) return 'unsupported';
  if (Notification.permission !== 'default') return Notification.permission;
  try {
    return await Notification.requestPermission();
  } catch {
    return Notification.permission;
  }
}

/** Text of a desktop notification; a simulated event says so in the title. */
export function notificationText(alert: Alert): { title: string; body: string } {
  return {
    title: alert.simulated ? `${SIMULATED_LABEL}: ${alert.title}` : alert.title,
    body: `${alert.entity_name}. ${alert.why_it_matters}`,
  };
}

/** Shows a desktop notification if allowed; returns false when it could not. */
export function showDesktopNotification(alert: Alert, onClick: () => void): boolean {
  if (!supported() || Notification.permission !== 'granted') return false;
  const { title, body } = notificationText(alert);
  try {
    const n = new Notification(title, { body, tag: alert.id, icon: '/favicon.svg' });
    n.onclick = () => {
      window.focus();
      onClick();
      n.close();
    };
    return true;
  } catch {
    return false;
  }
}
