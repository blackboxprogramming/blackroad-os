# Commands/

Human/operator command surface.

17 core commands and routing maps.

Commands call scripts and workflows. They should be operator-readable first.

## Network

`road network` is defined in `Commands/network.md` and implemented by `Products/road-network`.

```text
road network validate
road network discover
road network plan
road network apply
```

Network canon lives in `Canon/Network/`; provider state is read and reconciled against canon rather than becoming authority.
