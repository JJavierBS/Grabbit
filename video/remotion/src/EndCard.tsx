import React from 'react';
import {AbsoluteFill, Easing} from 'remotion';
import {Blur, C, FONT, OUTFIT, mix, ramp, spring, useT} from './theme';

// s12, film 110.3-115.5 s. The two speed lines bring the panel in, then they become the two
// bars of the mark: one object changes shape, nothing fades from one picture to the next.
const MARK = {left: 616, top: 330, height: 168}; // viewBox 115 290 410 370
const K = MARK.height / 370;
const bar = (x: number, y: number, w: number, h: number) => ({left: MARK.left + (x - 115) * K, top: MARK.top + (y - 290) * K, width: w * K, height: h * K});
const LINES = [
  {from: {top: 420, width: 640, height: 84}, to: bar(158, 487, 104, 28)},
  {from: {top: 540, width: 800, height: 86}, to: bar(122, 537, 128, 29)},
];
const NAME = 'Grabbit'.split('');
const CALA = ['Built', 'on', 'Cala'];

const Inner: React.FC = () => {
  const t = useT();
  // the lines enter first and lead the panel edge; the panel passes under them as they brake
  const panel = mix(2400, 0, ramp(t, 0.18, 0.6, Easing.inOut(Easing.cubic)));
  const rabbit = spring(t - 0.8, 0.78, 2.4);
  const cta = spring(t - 2.0, 0.8, 2.6);
  return (
    <AbsoluteFill style={{fontFamily: FONT, color: C.ink}}>
      <AbsoluteFill style={{background: C.ground, translate: `${panel}px 0`}} />
      {LINES.map(({from, to}, k) => {
        const go = ramp(t, k * 0.04, 0.85, Easing.inOut(Easing.cubic));
        const fold = ramp(t, 0.38 + k * 0.04, 0.5, Easing.out(Easing.cubic));
        const height = mix(from.height, to.height, fold);
        return (
          <div
            key={k}
            style={{
              position: 'absolute',
              left: mix(1920, to.left, go),
              top: mix(from.top, to.top, fold),
              width: mix(from.width, to.width, fold),
              height,
              borderRadius: height / 2,
              background: C.violet,
            }}
          />
        );
      })}
      <svg
        viewBox="115 290 410 370"
        style={{position: 'absolute', left: MARK.left, top: MARK.top, height: MARK.height, opacity: ramp(t, 0.8, 0.1), translate: `${mix(320, 0, rabbit)}px 0`}}
      >
        <mask id="cut">
          <rect x="0" y="0" width="1000" height="1000" fill="#fff" />
          <circle cx="385" cy="545" r="48" />
          <rect x="385" y="478" width="140" height="19" />
          <circle cx="452" cy="452" r="9" />
        </mask>
        <g fill={C.ink} mask="url(#cut)">
          <circle cx="395" cy="535" r="120" />
          <ellipse cx="342" cy="395" rx="105" ry="34" transform="rotate(21 342 395)" />
          <ellipse cx="400" cy="362" rx="107" ry="33" transform="rotate(35 400 362)" />
        </g>
      </svg>
      <div style={{position: 'absolute', left: MARK.left + 410 * K + 26, top: MARK.top, height: MARK.height, display: 'flex', alignItems: 'center', fontFamily: OUTFIT, fontWeight: 800, fontSize: 132, letterSpacing: '-.01em'}}>
        {NAME.map((ch, i) => {
          const p = ramp(t, 1.08 + i * 0.05, 0.16, Easing.out(Easing.quad));
          return (
            <span key={i} style={{display: 'inline-block', opacity: p, filter: `blur(${mix(6, 0, p)}px)`}}>
              {ch}
            </span>
          );
        })}
      </div>
      <div style={{position: 'absolute', left: 0, right: 0, top: 560, textAlign: 'center', fontSize: 52, fontWeight: 600}}>
        {CALA.map((w, i) => {
          const p = ramp(t, 1.68 + i * 0.08, 0.16, Easing.out(Easing.quad));
          return (
            <span key={i} style={{display: 'inline-block', marginRight: i < 2 ? '.26em' : 0, opacity: p, filter: `blur(${mix(6, 0, p)}px)`}}>
              {w}
            </span>
          );
        })}
      </div>
      <div
        style={{
          position: 'absolute',
          left: 630,
          top: 690,
          width: 660,
          height: 104,
          borderRadius: 20,
          background: C.ink,
          color: '#fff',
          fontSize: 42,
          fontWeight: 700,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          opacity: ramp(t, 2.0, 0.15),
          translate: `0 ${mix(28, 0, cta)}px`,
          scale: mix(0.94, 1, cta),
        }}
      >
        Try the demo
      </div>
    </AbsoluteFill>
  );
};

export const EndCard: React.FC = () => (
  <Blur>
    <Inner />
  </Blur>
);
