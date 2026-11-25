# VANTOR Lua examples

Lua 5.4.9 is the first programming language published in the Nyan x86_64 repository.

After installing it on a network-ready VANTOR system:

```sh
nyan update
nyan install lua
lua examples/lua/hello.lua
luac -p examples/lua/hello.lua
```

The package includes the `lua` interpreter, `luac` bytecode compiler, headers and static development library. The sample itself uses only the standard Lua runtime.
