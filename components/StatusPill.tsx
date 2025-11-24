import type { EnvStatus } from "../src/types";

const statusConfig: Record<EnvStatus, { label: string; className: string }> = {
  healthy: { label: "Healthy", className: "status-pill status-pill--healthy" },
  degraded: { label: "Degraded", className: "status-pill status-pill--degraded" },
  down: { label: "Down", className: "status-pill status-pill--down" }
};

interface StatusPillProps {
  status: EnvStatus;
}

export function StatusPill({ status }: StatusPillProps) {
  const config = statusConfig[status];
  return <span className={config.className}>{config.label}</span>;
}
