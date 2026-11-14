import type { components } from "./schema";

type Schemas = components["schemas"];

export type TrustLevel = Schemas["Fact"]["trust"];
export type Source = Schemas["Source"];
export type Fact = Schemas["Fact"];
export type Investor = Schemas["Investor"];
export type Round = Schemas["Round"];
export type Signal = Schemas["Signal"];
export type Candidate = Schemas["Candidate"];
export type Profile = Schemas["Profile"];
export type ProfileChange = Schemas["ProfileChange"];
export type ChatMessage = Schemas["ChatMessage"];
export type Report = Schemas["Report"];
export type ReportKind = Schemas["Report"]["kind"];
export type Alert = Schemas["Alert"];
export type Health = Schemas["Health"];
export type ErrorResponse = Schemas["ErrorResponse"];
