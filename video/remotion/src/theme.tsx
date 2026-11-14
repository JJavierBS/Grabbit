import React from 'react';
import {Easing, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {HtmlInCanvasMotionBlur} from '@remotion/motion-blur';
import {loadFont} from '@remotion/fonts';
import {loadFont as loadOutfit} from '@remotion/google-fonts/Outfit';

// The look is in ../../SPEC.md (LOOK, OBJECTS). Keep these values equal to the HyperFrames scenes.
export const C = {ground: '#f7f7fa', line: '#e3e3ec', ink: '#14151c', muted: '#5c5d6e', violet: '#6139f8'};
export const FONT = '"Hanken Grotesk", sans-serif';
export const OUTFIT = loadOutfit('normal', {weights: ['800'], subsets: ['latin']}).fontFamily;
loadFont({family: 'Hanken Grotesk', url: staticFile('hanken-grotesk.woff2'), weight: '100 900'});

export const PLATE: React.CSSProperties = {
  position: 'absolute',
  background: C.ground,
  border: `2px solid ${C.line}`,
  borderRadius: 22,
  boxShadow: '0 30px 70px rgba(20,21,28,.14)',
  fontFamily: FONT,
  color: C.ink,
};

/** Seconds on the clip clock. Fractional inside the motion blur, so each sample gets its own time. */
export const useT = () => useCurrentFrame() / useVideoConfig().fps;

/** Closed-form spring from 0 to 1. zeta is the damping ratio (0.7-0.85 reads premium), hz the speed. */
export const spring = (t: number, zeta = 0.8, hz = 2.6) => {
  if (t <= 0) return 0;
  const w = 2 * Math.PI * hz;
  if (zeta >= 1) return 1 - Math.exp(-w * t) * (1 + w * t);
  const wd = w * Math.sqrt(1 - zeta * zeta);
  return 1 - Math.exp(-zeta * w * t) * (Math.cos(wd * t) + ((zeta * w) / wd) * Math.sin(wd * t));
};

/** 0 to 1 between from and from + dur. The default ease is a long-tailed arrival. */
export const ramp = (t: number, from: number, dur: number, easing: (n: number) => number = Easing.out(Easing.exp)) =>
  interpolate(t, [from, from + dur], [0, 1], {easing, extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});

export const mix = (a: number, b: number, p: number) => a + (b - a) * p;

/** Real motion blur: the children render at sub-frame times and the samples are averaged. */
export const Blur: React.FC<{children: React.ReactNode; samples?: number}> = ({children, samples = 16}) => {
  const {width, height} = useVideoConfig();
  return (
    <HtmlInCanvasMotionBlur width={width} height={height} samples={samples} shutterAngle={180}>
      {children}
    </HtmlInCanvasMotionBlur>
  );
};

/** One odometer column. pos is the number of steps rolled: 13.0 shows a 3 after 13 steps. */
export const Roll: React.FC<{pos: number; size: number; blankZero?: boolean}> = ({pos, size, blankZero}) => {
  const h = size * 1.1;
  const last = Math.ceil(pos) + 1;
  return (
    <span style={{display: 'inline-block', position: 'relative', height: h, overflow: 'hidden', verticalAlign: 'top'}}>
      <span style={{visibility: 'hidden'}}>0</span>
      <span style={{position: 'absolute', left: 0, top: 0, translate: `0 ${-pos * h}px`}}>
        {Array.from({length: last + 1}, (_, i) => (
          <span key={i} style={{display: 'block', height: h}}>
            {blankZero && i === 0 ? '' : i % 10}
          </span>
        ))}
      </span>
    </span>
  );
};
