-- VANTOR Lua starter example
local version = _VERSION
local function greet(name)
    return ("Hello, %s! Welcome to VANTOR."):format(name)
end

print("Runtime: " .. version)
print(greet("developer"))
