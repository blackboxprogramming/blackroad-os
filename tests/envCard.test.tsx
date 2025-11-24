import { render, screen } from "@testing-library/react";
import React from "react";
import { EnvCard } from "../components/EnvCard";
import type { Environment } from "../src/types";

describe("EnvCard", () => {
  const env: Environment = {
    id: "env_123",
    name: "Production",
    region: "us-west-2",
    status: "healthy"
  };

  it("renders name, region, and id", () => {
    render(<EnvCard env={env} />);
    expect(screen.getByText(env.region)).toBeInTheDocument();
    expect(screen.getByText(env.name)).toBeInTheDocument();
    expect(screen.getByText(`Env ID: ${env.id}`)).toBeInTheDocument();
  });
});
