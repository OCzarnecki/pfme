# PFME

Personal finance modeling engine.

Works by specifying "scenarios" which are descriptions of simulation parameters. A scenario is a python file with a `get_config` function. The function must take no arguments and return an instance of
`SimulationConfig`.
