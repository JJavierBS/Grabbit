import React from 'react';
import {AbsoluteFill} from 'remotion';
import {Blur, C, PLATE, Roll, mix, ramp, spring, useT} from './theme';

// s01, film 4.7-10.5 s: "more than 3,000 startups" is spoken at film 4.6 s.
const SIZE = 150;
// [steps rolled, seconds]: the right column rolls the longest, so the number settles left to right
const COLUMNS: [number, number][] = [[13, 0.55], [20, 0.7], [30, 0.85], [40, 1.0]];

const Inner: React.FC = () => {
  const t = useT();
  const land = spring(t - 0.05, 0.8, 2.6);
  const plus = spring(t - 1.1, 0.6, 3.2);
  return (
    <AbsoluteFill>
      <div
        style={{
          ...PLATE,
          left: 1236,
          top: 290,
          width: 588,
          padding: '30px 40px 34px',
          opacity: ramp(t, 0.05, 0.2),
          translate: `0 ${mix(40, 0, land)}px`,
          scale: mix(0.96, 1, land),
        }}
      >
        <div style={{fontSize: SIZE, fontWeight: 800, letterSpacing: '-.04em', lineHeight: 1.1, whiteSpace: 'nowrap', fontVariantNumeric: 'tabular-nums', height: SIZE * 1.1, marginTop: -8, maskImage: 'linear-gradient(#0000, #000 14%, #000 88%, #0000)'}}>
          {COLUMNS.map(([steps, dur], i) => (
            <React.Fragment key={i}>
              <Roll pos={steps * ramp(t, 0.15, dur)} size={SIZE} />
              {i === 0 ? ',' : null}
            </React.Fragment>
          ))}
          <span style={{display: 'inline-block', opacity: ramp(t, 1.1, 0.12), scale: mix(0.4, 1, plus), transformOrigin: '30% 60%'}}>+</span>
        </div>
        <div style={{fontSize: 44, fontWeight: 600, letterSpacing: '-.02em', lineHeight: 1.2, color: C.muted, marginTop: 10}}>startups through these doors</div>
      </div>
    </AbsoluteFill>
  );
};

export const Count: React.FC = () => (
  <Blur samples={32}>
    <Inner />
  </Blur>
);
