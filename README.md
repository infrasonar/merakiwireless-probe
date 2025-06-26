[![CI](https://github.com/infrasonar/merakiwireless-probe/workflows/CI/badge.svg)](https://github.com/infrasonar/merakiwireless-probe/actions)
[![Release Version](https://img.shields.io/github/release/infrasonar/merakiwireless-probe)](https://github.com/infrasonar/merakiwireless-probe/releases)

# InfraSonar Meraki Wireless Device Probe

Documentation: https://docs.infrasonar.com/collectors/probes/meraki/

## Environment variable

Variable            | Default                        | Description
------------------- | ------------------------------ | ------------
`AGENTCORE_HOST`    | `127.0.0.1`                    | Hostname or Ip address of the AgentCore.
`AGENTCORE_PORT`    | `8750`                         | AgentCore port to connect to.
`INFRASONAR_CONF`   | `/data/config/infrasonar.yaml` | File with probe and asset configuration like credentials.
`MAX_PACKAGE_SIZE`  | `500`                          | Maximum package size in kilobytes _(1..2000)_.
`MAX_CHECK_TIMEOUT` | `300`                          | Check time-out is 80% of the interval time with `MAX_CHECK_TIMEOUT` in seconds as absolute maximum.
`DRY_RUN`           | _none_                         | Do not run demonized, just return checks and assets specified in the given yaml _(see the [Dry run section](#dry-run) below)_.
`LOG_LEVEL`         | `warning`                      | Log level (`debug`, `info`, `warning`, `error` or `critical`).
`LOG_COLORIZED`     | `0`                            | Log using colors (`0`=disabled, `1`=enabled).
`LOG_FMT`           | `%y%m%d %H:%M:%S`              | Log format prefix.


## API key

The `secret` will be used as `X-Cisco-Meraki-API-Key` in the header for HTTP calls.

```yaml
meraki:
  config:
    secret: 'xxxxxxxxxxx'
```

## Docker build

```
docker build -t merakiwireless-probe . --no-cache
```

## Dry run

Available checks:
- `device`

Create a yaml file, for example _(test.yaml)_:

```yaml
asset:
  name: "MerakiDevice"
  check: "device"
  config:
    id: "123456"
    serial: "ABCD-123"
```

> Note: `id` is the Organization ID

Run the probe with the `DRY_RUN` environment variable set the the yaml file above.

```
DRY_RUN=test.yaml python main.py
```
