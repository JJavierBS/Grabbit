import type { components } from "./schema";

type Schemas = components["schemas"];

export type TrustLevel = Schemas["Fact"]["trust"];
export type Source = Schemas["Source"];
export type Fact = Schemas["Fact"];
export type Investor = Schemas["Investor"];
export type Round = Schemas["Round"];
export type Signal = Schemas["Signal"];
export type HiddenLink = Schemas["HiddenLink"];
export type LinkNode = Schemas["LinkNode"];
export type Candidate = Schemas["Candidate"];
export type NewsItem = Schemas["NewsItem"];
export type NewsEntity = Schemas["NewsEntity"];
export type Profile = Schemas["Profile"];
export type ProfileChange = Schemas["ProfileChange"];
export type ChatMessage = Schemas["ChatMessage"];
export type ExploredGraph = Schemas["ExploredGraph"];
export type GraphNode = Schemas["GraphNode"];
export type GraphEdge = Schemas["GraphEdge"];
export type Report = Schemas["Report"];
export type ReportKind = Schemas["Report"]["kind"];
export type Alert = Schemas["Alert"];
export type Health = Schemas["Health"];
export type ErrorResponse = Schemas["ErrorResponse"];

/** One value of a Fact; a list value holds several of these. */
export type FactScalar = Exclude<Fact["value"], unknown[] | null>;
