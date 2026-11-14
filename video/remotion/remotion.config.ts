import {Config} from '@remotion/cli/config';

// Transparent WebM: the clips sit over the footage in ../index.html
Config.setVideoImageFormat('png');
Config.setPixelFormat('yuva420p');
Config.setCodec('vp9');
Config.setOverwriteOutput(true);
