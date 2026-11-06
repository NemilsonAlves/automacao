export type Environment = "development" | "test" | "staging" | "production";

export interface LivenessResponse {
  status: "ok";
}

export interface ReadinessResponse {
  status: "ready" | "unavailable";
  database: "ok" | "unavailable";
}
