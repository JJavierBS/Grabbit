import { screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { App, CONFIRM_MESSAGE } from './App';
import type { ChatMessage } from './api/types';
import { chatV2, historyV2, profileV2, reportV1, reportV2 } from './dev/fixtures';
import { formatChangeValue } from './features/profile/ProfileHistory';
import { mockApi, renderWithClient } from './test/renderApp';

const base = {
  'GET /api/profile': () => profileV2,
  'GET /api/profile/history': () => historyV2,
  'GET /api/chat': () => chatV2,
  'GET /api/alerts': () => [],
};

describe('App', () => {
  it('shows the report with trust badges beside the chat', async () => {
    mockApi({ ...base, 'GET /api/reports/latest': () => reportV1 });
    renderWithClient(<App />);
    expect(
      await screen.findByRole('heading', { name: 'Slush 2026 prep report' }),
    ).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Northwind Labs' })).toBeInTheDocument();
    expect(screen.getAllByText('Official filing').length).toBeGreaterThan(0);
    expect(await screen.findByText(/Tell me what you look for/)).toBeInTheDocument();
  });

  it('shows an error with a retry when the report fails, never a blank screen', async () => {
    mockApi({
      ...base,
      'GET /api/reports/latest': {
        status: 500,
        body: { error: { code: 'boom', message: 'Cala timed out.' } },
      },
    });
    renderWithClient(<App />);
    expect(await screen.findByText('The report did not load')).toBeInTheDocument();
    expect(screen.getByText('Cala timed out.')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Try again' })).toBeInTheDocument();
  });

  it('highlights what changed when a correction rewrites the report', async () => {
    let report = reportV1;
    const reply: ChatMessage = {
      id: 'm9',
      role: 'agent',
      text: 'From now on: shorter reports, co-investors first. I rewrote your report.',
      created_at: '2026-11-14T09:34:00Z',
      profile_changes: [],
    };
    const calls = mockApi({
      ...base,
      'GET /api/reports/latest': () => report,
      'POST /api/chat': () => {
        report = reportV2;
        return reply;
      },
    });
    renderWithClient(<App />);
    await screen.findByRole('heading', { name: 'Slush 2026 prep report' });

    await userEvent.type(
      screen.getByRole('textbox', { name: 'Message Grabbit' }),
      'Shorter, co-investors first{Enter}',
    );

    const banner = await screen.findByText(/Rewritten for you/);
    expect(banner.parentElement).toHaveTextContent('2 sections moved');
    expect(screen.getByText('Rounds and leads').tagName).toBe('S');
    const section = screen
      .getByRole('heading', { name: 'Co-investors you trust' })
      .closest('section');
    expect(section).toHaveAttribute('data-changed', 'moved');
    expect(within(section as HTMLElement).getByText('Moved')).toBeInTheDocument();
    expect(calls.find((c) => c.key === 'POST /api/chat')?.body).toEqual({
      text: 'Shorter, co-investors first',
    });
  });

  it('confirms the report by telling the agent', async () => {
    const calls = mockApi({
      ...base,
      'GET /api/reports/latest': () => reportV1,
      'POST /api/chat': () => ({ ...chatV2[0], id: 'm10' }),
    });
    renderWithClient(<App />);
    await userEvent.click(
      await screen.findByRole('button', { name: 'Looks right, keep me posted' }),
    );
    expect(calls.find((c) => c.key === 'POST /api/chat')?.body).toEqual({ text: CONFIRM_MESSAGE });
    expect(await screen.findByRole('button', { name: 'Watching your shortlist' })).toBeDisabled();
  });

  it('opens the profile history with the reason for each change', async () => {
    mockApi({ ...base, 'GET /api/reports/latest': () => reportV1 });
    renderWithClient(<App />);
    await userEvent.click(screen.getByRole('button', { name: 'What changed' }));
    expect(await screen.findByText('You said you trust these two investors.')).toBeInTheDocument();
    expect(
      screen.getByText(
        'Plain language. One paragraph per startup. Lead with the round and who led it.',
      ),
    ).toBeInTheDocument();
  });
});

describe('formatChangeValue', () => {
  it('reads empty, lists, objects and enum values in plain words', () => {
    expect(formatChangeValue(null)).toBe('nothing');
    expect(formatChangeValue([])).toBe('nothing');
    expect(formatChangeValue(['pre_seed', 'seed'])).toBe('pre seed, seed');
    expect(formatChangeValue([{ entity_id: 'x', name: 'Aurora Ventures' }])).toBe(
      'Aurora Ventures',
    );
    expect(formatChangeValue({ value: 25000, unit: 'EUR' })).toBe('25000');
  });
});
