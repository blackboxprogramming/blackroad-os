import { render, screen } from "@testing-library/react";
import React from "react";
import { StatusPill } from "../components/StatusPill";
import type { EnvStatus } from "../src/types";

describe("StatusPill", () => {
  const cases: [EnvStatus, string, string][] = [
    ["healthy", "Healthy", "status-pill--healthy"],
    ["degraded", "Degraded", "status-pill--degraded"],
    ["down", "Down", "status-pill--down"]
  ];

  it.each(cases)("renders %s status", (status, label, className) => {
    render(<StatusPill status={status} />);
    const pill = screen.getByText(label);
    expect(pill).toBeInTheDocument();
    expect(pill.className).toContain(className);
  });
});
