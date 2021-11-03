Welcome to EasyTest, a testing framework for PHP.

EasyTest attempts to minimize boilerplate while remaining latitudinarian about
how you write your tests. To this end, tests are normal PHP functions and
classes, and anything whose name starts with `test` is automatically
discovered and run. Other features include: support of PHP's `assert`
function, subtests, test dependencies, hierarchical management of test
fixture, and multiple execution of tests with parameterized arguments.

In addition to this wiki, you may also want to consult the
[README](https://github.com/gnarlyquack/easytest).

# Contents

1. [Getting Started](@getting-started)
   will get you up and running with EasyTest.
2. [Writing Tests](@writing-tests)
   tells you everything you need to know about writing tests.
3. [Test Fixtures](@test-fixtures)
   explains how EasyTest lets you to manage your tests' state.
4. [Writing Assertions](@writing-assertions)
   provides a comprehensive example on how to implement your own assertion if
   EasyTest doesn't provide the assertion you want and/or using PHP's `assert`
   is impractical.
