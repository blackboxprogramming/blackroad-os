import type { Environment } from "../src/types";
import { StatusPill } from "./StatusPill";

interface EnvCardProps {
  env: Environment;
}

export function EnvCard({ env }: EnvCardProps) {
  return (
    <div className="env-card">
      <div className="env-region" style={{ textTransform: "uppercase", fontSize: "0.85rem" }}>
        {env.region}
      </div>
      <h2>{env.name}</h2>
      <div>Env ID: {env.id}</div>
      <StatusPill status={env.status} />
    </div>
  );
}
