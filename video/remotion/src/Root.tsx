import React from 'react';
import {Composition} from 'remotion';
import {Count} from './Count';
import {EndCard} from './EndCard';
import {Pile} from './Pile';

// One composition for each overlay clip. The start of each clip on the film clock is in ../index.html.
const clip = {fps: 30, width: 1920, height: 1080};

export const Root: React.FC = () => (
  <>
    <Composition id="Count" component={Count} durationInFrames={174} {...clip} />
    <Composition id="Pile" component={Pile} durationInFrames={210} {...clip} />
    <Composition id="EndCard" component={EndCard} durationInFrames={156} {...clip} />
  </>
);
