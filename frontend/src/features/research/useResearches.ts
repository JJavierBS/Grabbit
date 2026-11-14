import { useSyncExternalStore } from "react";
import { researchSnapshot, subscribeResearches } from "../../api/workspace";

/** This browser's researches and the current one, re-rendering when either changes. */
export const useResearches = () => useSyncExternalStore(subscribeResearches, researchSnapshot);
