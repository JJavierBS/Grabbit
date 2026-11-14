import React from 'react';
import {AbsoluteFill, Easing} from 'remotion';
import {Blur, C, FONT, PLATE, Roll, mix, ramp, spring, useT} from './theme';

// s02 and the first second of s03, film 13.1-20.1 s. The clip crosses the hard cut at 6.0 s.
// "open one tab" film 13.3 s, "per business" 15.1 s, "still searching" 18.1 s, "there's a way" 19.45 s.
const CUT = 6;
const SIZE = 100;
// [left, top, tab title, body line widths in %]
const WINS: [number, number, string, number[]][] = [
  [1010, 90, 'seed round 2025', [69, 75, 77, 49]],
  [1330, 60, 'who invested in', [76, 82, 84, 60]],
  [1150, 250, 'founder background', [83, 69, 91, 41]],
  [980, 420, 'is it at Slush?', [90, 76, 76, 52]],
  [1350, 330, 'pitch deck pdf', [67, 83, 83, 63]],
  [1090, 560, 'team size', [74, 70, 90, 44]],
  [1300, 520, 'last valuation', [81, 77, 75, 55]],
  [1040, 170, 'press: raises', [88, 84, 82, 66]],
  [1360, 150, 'investor list', [65, 71, 89, 47]],
  [1200, 400, 'portfolio page', [72, 78, 74, 58]],
  [960, 300, 'funding news', [79, 85, 81, 39]],
  [1320, 610, 'lead investor?', [86, 72, 88, 50]],
];
const LAND = [0.1, 0.7, 1.2, 1.65, 2.05, 2.4, 2.7, 2.95, 3.2, 3.4, 3.6, 3.8]; // a window lands
const TABS = [4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 47]; // tabs open after it

/** Seeded 0-1 value, so each render is the same. */
const rnd = (i: number, k: number) => {
  const v = Math.sin(i * 12.9898 + k * 78.233) * 43758.5453;
  return v - Math.floor(v);
};
// The speed lines push from the left: the windows leave in the order of their left edge.
const RANK = WINS.map((w, i) => WINS.filter((o) => o[0] < w[0]).length + i * 0.01);
const sweep = (t: number, rank: number) => ramp(t, CUT + 0.36 + rank * 0.014, 0.42, Easing.in(Easing.cubic));

const Win: React.FC<{i: number; t: number}> = ({i, t}) => {
  const [left, top, title, lines] = WINS[i];
  const p = spring(t - LAND[i], 0.68 + 0.2 * rnd(i, 1), 2.4);
  const rest = (rnd(i, 2) - 0.5) * 4;
  // each later window that lands gives this one a small push away from it
  let nx = 0;
  let ny = 0;
  for (let j = i + 1; j < WINS.length; j++) {
    const tau = t - LAND[j];
    if (tau <= 0) break;
    const bump = Math.exp(-9 * tau) * Math.sin(20 * tau) * 7;
    const dx = left - WINS[j][0];
    const dy = top - WINS[j][1];
    const d = Math.hypot(dx, dy) || 1;
    nx += (dx / d) * bump;
    ny += (dy / d) * bump;
  }
  const out = sweep(t, RANK[i]);
  return (
    <div
      style={{
        position: 'absolute',
        left,
        top,
        width: 500,
        height: 310,
        background: '#fff',
        border: `2px solid ${C.line}`,
        borderRadius: 22,
        boxShadow: '0 30px 70px rgba(20,21,28,.14)',
        overflow: 'hidden',
        opacity: ramp(t, LAND[i], 0.1),
        translate: `${mix(260, 0, p) + nx + 1300 * out}px ${mix(60 * (rnd(i, 3) - 0.3), 0, p) + ny}px`,
        rotate: `${mix(rest + 9, rest, p) + 6 * out}deg`,
        scale: mix(0.88, 1, p),
      }}
    >
      <div style={{height: 50, background: '#f0eff5', borderBottom: `2px solid ${C.line}`, display: 'flex', alignItems: 'flex-end', gap: 6, padding: '0 16px'}}>
        {[0, 1, 2].map((d) => (
          <i key={d} style={{width: 12, height: 12, borderRadius: '50%', background: '#c9c9d6', alignSelf: 'center', flex: 'none', marginRight: d === 2 ? 10 : 0}} />
        ))}
        <span style={{height: 36, width: 186, borderRadius: '10px 10px 0 0', background: '#fff', padding: '0 12px', fontSize: 20, fontWeight: 500, lineHeight: '36px', color: C.muted, whiteSpace: 'nowrap', overflow: 'hidden', flex: 'none', boxSizing: 'border-box'}}>{title}</span>
        {[0, 1, 2].slice(0, i === 11 ? 2 : 3).map((d) => (
          <span key={d} style={{height: 36, width: 62, borderRadius: '10px 10px 0 0', background: C.line, flex: 'none'}} />
        ))}
      </div>
      <div style={{padding: '26px 28px', display: 'flex', flexDirection: 'column', gap: 16}}>
        {lines.map((w, k) => (
          <b key={k} style={{display: 'block', width: `${w}%`, height: k ? 14 : 22, borderRadius: 11, background: k ? C.line : '#c9c9d6'}} />
        ))}
      </div>
    </div>
  );
};

const Inner: React.FC = () => {
  const t = useT();
  // the count follows the windows; the columns roll, they do not swap
  let v = 1;
  TABS.forEach((n, k) => {
    v += (n - (k ? TABS[k - 1] : 1)) * ramp(t, LAND[k], 0.3, Easing.out(Easing.cubic));
  });
  const tens = Math.floor(v / 10) + Math.min(1, Math.max(0, (v % 10) - 9));
  const land = spring(t - 0.3, 0.8, 2.6);
  const out = sweep(t, 1);
  const zero = ramp(t, 4.5, 0.2, Easing.out(Easing.quad));
  const line: React.CSSProperties = {fontSize: SIZE, fontWeight: 800, letterSpacing: '-.04em', lineHeight: 1.1, whiteSpace: 'nowrap', fontVariantNumeric: 'tabular-nums'};
  return (
    <AbsoluteFill style={{fontFamily: FONT}}>
      {WINS.map((_, i) => (
        <Win key={i} i={i} t={t} />
      ))}
      <div
        style={{
          ...PLATE,
          left: 1010,
          top: 730,
          padding: '22px 38px 28px',
          opacity: ramp(t, 0.3, 0.2),
          translate: `${1300 * out}px ${mix(40, 0, land)}px`,
          rotate: `${6 * out}deg`,
          scale: mix(0.96, 1, land),
        }}
      >
        <div style={{...line, height: SIZE * 1.1}}>
          <span style={{display: 'inline-block', overflow: 'hidden', verticalAlign: 'top', maxWidth: Math.min(1, tens) * SIZE * 0.66}}>
            <Roll pos={tens} size={SIZE} blankZero />
          </span>
          <Roll pos={v} size={SIZE} /> tabs.
        </div>
        <div style={{...line, color: C.violet, opacity: zero, filter: `blur(${mix(8, 0, zero)}px)`}}>0 decisions.</div>
      </div>
      {/* the two speed lines of the logo take the pile away */}
      {[
        [1000, 400, 640, 84],
        [940, 520, 800, 86],
      ].map(([left, top, width, height], k) => (
        <div
          key={k}
          style={{
            position: 'absolute',
            left,
            top,
            width,
            height,
            borderRadius: height / 2,
            background: C.violet,
            transformOrigin: '0% 50%',
            translate: `${1300 * ramp(t, CUT + 0.32 + k * 0.04, 0.4, Easing.in(Easing.quad))}px 0`,
            scale: `${ramp(t, CUT + 0.16 + k * 0.04, 0.16, Easing.out(Easing.quad))} 1`,
          }}
        />
      ))}
    </AbsoluteFill>
  );
};

export const Pile: React.FC = () => (
  <Blur>
    <Inner />
  </Blur>
);
