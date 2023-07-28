# Performance

Dash Express takes care of improving performance instead of you, here are the ways built in by default:

## Using callbacks on the client side
Most of the callbacks are implemented on the client side, not on the server in Python.

## Partial property updates
Graph creation functions are automatically converted to Patch objects, only updating the parts of a property that you want to change

## Caching
Dash Express uses the `Flash-Caching` library, which stores the results in a shared memory database such as Redis, or as a file in your file system.

## Data Serialization with orjson
DashExpress uses `orjson` to speed up serialization to JSON and in turn improve your callback performance