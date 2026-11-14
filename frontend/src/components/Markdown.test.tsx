import { render, screen } from '@testing-library/react';
import { Markdown } from './Markdown';

describe('Markdown', () => {
  it('renders paragraphs, lists, bold, italic and links', () => {
    const { container } = render(
      <Markdown
        source={'Intro with **bold** and *soft*.\n\n- one\n- [two](https://example.com)'}
      />,
    );
    expect(container.querySelectorAll('p')).toHaveLength(1);
    expect(screen.getByText('bold').tagName).toBe('STRONG');
    expect(screen.getByText('soft').tagName).toBe('EM');
    expect(screen.getAllByRole('listitem')).toHaveLength(2);
    expect(screen.getByRole('link', { name: 'two' })).toHaveAttribute(
      'href',
      'https://example.com',
    );
  });

  it('never renders raw HTML or unsafe links', () => {
    const { container } = render(
      <Markdown source={'<img src=x onerror=alert(1)> [x](javascript:alert(1))'} />,
    );
    expect(container.querySelector('img')).toBeNull();
    expect(screen.queryByRole('link')).not.toBeInTheDocument();
    expect(container.textContent).toContain('<img src=x onerror=alert(1)>');
  });
});
