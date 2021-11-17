# Writing Tests

## What is a Test?

Starting from the current working directory, Dr. Strangetest automatically
discovers your tests using the following rules. All names are discovered
without regard to case.

-   Any directory whose name begins with `test` is entered and recursively
    searched for additional tests.
-   Any file whose name begins with `test` and has file extension `.php` is
    included and searched for test functions and classes. A file may contain
    any number of test classes and/or test functions.
-   Any class whose name begins with `test` is searched for test methods. If
    any are found, an instance of the class is instantiated and its test
    methods are run.
-   Any function or method whose name begins with `test` is run.

Directories, files, and classes are typically only visited once. However, it is
possible that multiple visits may be required in order to complete all tests
(usually because [test dependencies](@#test-dependencies) are involved). In
this case, there are a few things to keep in mind:

-   A file is only ever included once.

-   A new class instance is instantiated on every visit and disposed of when
    the visit is complete.

-   [Fixture functions](@test-fixtures#fixture-functions) are run on every
    visit.


Here's what writing tests with Dr. Strangetest might look like:

```php
<?php
// test_greet.php

use example\greet\GoodBye;
use example\greet\Hello;
use function strangetest\assert_identical;

function test_hello_to_the_world()
{
    $hello = new Hello;
    assert_identical('Hello, world!', $hello->greet());
}

function test_hello_to_humans()
{
    $hello = new Hello;
    assert_identical('Hello, human!', $hello->greet('human'));
}

function test_goodbye_to_the_world()
{
    $adieu = new GoodBye;
    assert_identical('Goodbye, cruel world!', $adieu->bid());
}

function test_goodbye_to_humans()
{
    $adieu = new GoodBye;
    assert_identical('Goodbye, human!', $adieu->bid('human'));
}
```

Assuming you have written the code to make these tests pass, the result of
running your tests will look something like:

    $ strangetest
    Dr. Strangetest

    ....


    Seconds elapsed: 0
    Memory used: 1.273 MB
    Passed: 4

Alternatively, you might decide to group your tests into different classes and
files:

```php
<?php
// tests/test_hello.php

use example\greet\Hello;
use function strangetest\assert_identical;

class TestHello
{
    public function TestHelloToTheWorld()
    {
        $hello = new Hello;
        assert_identical('Hello, world!', $hello->greet());
    }

    public function TestHelloToHumans()
    {
        $hello = new Hello;
        assert_identical('Hello, human!', $hello->greet('human'));
    }
}
```
```php
<?php
// tests/test_goodbye.php

use example\greet\GoodBye;
use function strangetest\assert_identical;

class TestGoodBye
{
    function TestGoodByeToTheWorld()
    {
        $adieu = new GoodBye;
        assert_identical('Goodbye, cruel world!', $adieu->bid());
    }

    function TestGoodByeToHumans()
    {
        $adieu = new GoodBye;
        assert_identical('Goodbye, human!', $adieu->bid('human'));
    }
}
```

And checking with Dr. Strangetest:

    $ strangetest
    Dr. Strangetest

    ....


    Seconds elapsed: 0
    Memory used: 1.273 MB
    Passed: 4


## Making Assertions

A test "passes" unless an assertion fails or an error happens. Failures and
errors are signalled by throwing an exception. This means a test typically ends
immediately when a failure or an error happens.

Failed assertions are exceptions that are instances of `strangetest\Failure`.
In PHP 7 and higher, this is a subclass of PHP's built-in `AssertionError`
exception. Any other exception is treated as an error.

Although prior examples use assertions provided by Dr. Strangetest, you can
also use PHP's built-in `assert` function. Failed assertions are automatically
converted into exceptions as described above, and in PHP 7.2 and higher
`assert.exception` is automatically enabled.

```php
function testHelloToTheWorld()
{
    $hello = new Hello;
    assert('Hello, world!' === $hello->greet());
}
```

Dr. Strangetest's assertions will generally provide more detailed information
about why the assertion failed than PHP's `assert` does, but they are by no
mean comprehensive. `assert` provides a means to make any assertion you want,
although [writing your own assertions](@writing-assertions) is also
straightforward.

A full list of Dr. Strangetest's assertions is listed in the
[README](https://github.com/gnarlyquack/strangetest).


## Testing Exceptions and Errors

Although nothing stops you from using `try` and `catch` to test for exceptions,
`strangetest\assert_throws` tries to simplify the process. The function takes
the name of an expected exception and a callable and fails if invoking the
callable doesn't result in the expected exception being thrown, otherwise it
returns the exception instance.

```php
function test_division_by_zero()
{
    $actual = strangetest\assert_throws(
        DivisionByZeroError::class,
        function() { return 3 / 0; }
    );
    strangetest\assert_identical(
        'Division by zero', $actual->getMessage()
    );
}
```

Testing for errors is exactly the same, as (non-fatal) PHP errors are
automatically converted into an `ErrorException` and thrown. In fact, the above
test will fail in PHP 7.4 and earlier, because division by zero triggers a
warning error instead of throwing an exception. To make the test pass across
multiple versions of PHP, you might update the test as follows:

```php
function test_division_by_zero()
{
    $expected = version_compare(PHP_VERSION, '8.0', '<')
              ? ErrorException::class
              : DivisionByZeroError::class;

    $actual = strangetest\assert_throws(
        $expected,
        function() { return 3 / 0; }
    );
    strangetest\assert_identical(
        'Division by zero', $actual->getMessage()
    );
}
```


## Skipping Tests


### Skipping a Test

Your test suite might want to skip tests if it determines those tests are
incapable of being run, e.g., a version requirement isn't met or an extension
isn't enabled. For this, use the function `strangetest\skip`.

```php
strangetest\skip(string $reason): never
```

`$reason` is a string explaining why a test is being skipped.

No value is returned. This function unconditionally throws an instance of
`strangetest\Skip`.

Here's an example of how this might be used in your tests:


```php
function test_skip()
{
    if (version_compare(PHP_VERSION, MAX_VERSION) >= 0)
    {
        strangetest\skip('PHP version must be less than ' . MAX_VERSION);
    }

    // The actual test goes here. This is never reached if the version
    // requirement isn't met.
}
```

The resulting test run might look something like:

    $ strangetest
    Dr. Strangetest

    ........S.


    This report omitted skipped tests.
    To view, rerun Dr. Strangetest with the --verbose option.

    Seconds elapsed: 0.003
    Memory used: 1.211 MB
    Passed: 9, Skipped: 1


### Viewing Skipped Tests

Although the final test reports indicates tests were skipped during the test
run, details are not normally shown. Since you will likely be running the test
suite repeatedly, showing details about expected skipped tests usually just
clutters the report. Run Dr. Strangetest in verbose mode to see what tests were
skipped and why:

    $ strangetest --verbose
    Dr. Strangetest

    ........S.


    SKIPPED: test_skip
    PHP version must be less than 7.2
    in test_skip.php on line 7



    Seconds elapsed: 0.003
    Memory used: 1.211 MB
    Passed: 9, Skipped: 1


## Subtests

Subtests ensure a test continues even if an assertion fails. This can be useful
if you want to exercise a single test repeated with multiple data sets, or if
the outcome of several assertions can give a better idea of why a particular
assertion failed. Dr. Strangetest implements this through the
`strangetest\Context` interface, an instance of which is provided as the last
argument to every test function and test method.

```php
public strangetest\Context::subtest(callable $callback): bool
```

`$callback` is a callable that should take no parameters and return `void`.

A boolean is returned indicating if `$callback` passed or failed. `$callback`
fails if invoking it triggers an assertion failure. Other errors and exceptions
are not guarded against.

A test that uses subtests only passes if all subtests pass. If any subtest
fails, all failures are shown in the test report.

Revisiting an earlier example, perhaps you've decided you want a different
greeting based on the time of day. It might be tempting to write:

```php
function test_greetings()
{
    $greetings = [
        [new MorningGreet, 'Good morning, world!'],
        [new AfternoonGreet, 'Good afternoon, world!'],
        [new EveningGreet, 'Good evening, world!'],
        [new NightGreet, 'Good night, world!'],
    ];

    foreach ($greetings as [$greeter, $expected]) {
        strangetest\assert_identical($expected, $greeter->greet());
    }
}
```

The problem is, if any test fails, the next test isn't run.

    $ strangetest
    Dr. Strangetest

    F


    FAILED: test_greetings
    Assertion "$expected === $actual" failed

    - $expected
    + $actual

    - 'Good morning, world!'
    + 'Hello, world!'

    in test_greetings.php on line 14



    Seconds elapsed: 0
    Memory used: 1.273 MB
    Failed: 1


By using subtests, you can ensure the test is run for all data sets.

```php
function test_greetings(strangetest\Context $context)
{
    $greetings = [
        [new MorningGreet, 'Good morning, world!'],
        [new AfternoonGreet, 'Good afternoon, world!'],
        [new EveningGreet, 'Good evening, world!'],
        [new NightGreet, 'Good night, world!'],
    ];

    foreach ($greetings as $greeting)
    {
        $context->subtest(
            function () use ($greeting)
            {
                [$greeter, $expected] = $greeting;
                strangetest\assert_identical($expected, $greeter->greet());
            }
        );
    }
}
```

Now you can see all failures:

    $ strangetest
    Dr. Strangetest

    FFFF


    FAILED: test_greetings
    Assertion "$expected === $actual" failed

    - $expected
    + $actual

    - 'Good morning, world!'
    + 'Hello, world!'

    in test_greetings_subtest.php on line 20



    FAILED: test_greetings
    Assertion "$expected === $actual" failed

    - $expected
    + $actual

    - 'Good afternoon, world!'
    + 'Hello, world!'

    in test_greetings_subtest.php on line 20



    FAILED: test_greetings
    Assertion "$expected === $actual" failed

    - $expected
    + $actual

    - 'Good evening, world!'
    + 'Hello, world!'

    in test_greetings_subtest.php on line 20



    FAILED: test_greetings
    Assertion "$expected === $actual" failed

    - $expected
    + $actual

    - 'Good night, world!'
    + 'Hello, world!'

    in test_greetings_subtest.php on line 20



    Seconds elapsed: 0
    Memory used: 1.273 MB
    Failed: 4


## Test Dependencies

Test dependencies allow a test (the "dependent") to require one or more other
tests ("prerequisites") to first pass before the dependent is executed. If any
prerequisite is not successful, the dependent is skipped. Prerequisites may
also provide a test result for dependents to use in their own tests, although
there is no requirement for a prerequisite to do so.

Dr. Strangetest implements this through the `strangetest\Context` interface, an
instance of which is provided as the last argument to every test function and
test method. The interface provides two methods: `set` and `requires`. `set`
allows prerequisites to [save a result value](@#setting-a-test-result), and
`requires` allows dependents to [declare
dependencies](@#declaring-dependencies) on prerequisites and retrieve any saved
result a prerequisite may have saved.

```php
<?php

function test_one(strangetest\Context $context)
{
    $context->set(1);
}

function test_two(strangetest\Context $context)
{
    $actual = $context->requires('test_one');
    strangetest\assert_identical(1, $actual);
}

function test_three(strangetest\Context $context)
{
    $context->set(3);
}

function test_four(strangetest\Context $context)
{
    $state = $context->requires('test_one', 'test_two', 'test_three');
    strangetest\assert_identical(
        ['test_one' => 1, 'test_three' => 3],
        $state
    );
}
```


### Declaring Dependencies

The `strangetest\Context::requires` method lets a test declare a dependency on
one or more prerequisites and retrieve any result they may have saved.

```php
public strangetest\Context::requires(string ...$names): mixed
```

`$names` is one or more [test function names provided as a
string](@#specifying-test-names). At least one name must be provided.

Depending on the state of the provided names, one of the following is returned:
-   If one or more of the tests specified in `$names` has failed, an instance
    of `strangetest\Skip` is thrown.
-   If one or more of the tests specified in `$names` has not been run, an
    instance of `strangetest\Postpone` is thrown. The calling function will be
    run again at some point after all prerequisites have been run.
-   If `$names` contains only one test name and the test saved a result, the
    result is returned.
-   If `$names` contains multiple test names and any of the tests saved a
    result, an array is returned that maps each test name to its result. Array
    indices will match the names in `$names`, although only tests that saved a
    result are included in the array.
-   If none of the tests in `$names` saved a result, `null` is returned.


### Setting a Test Result

The `strangetest\Context::set` method lets prerequisites save a result for
dependents to use.

```php
public strangetest\Context::set(mixed $value): void
```

`$value` is the result value to save. The method does not return a value.

The method may be called at any time during a test and may also be called
multiple times, however only the final result value is saved.

You should be wary about the type of value being saved as a test result. There
is no special handling of it, it is simply saved and passed on to dependents.
Ideally, it should be a standalone value that has no dependency on external
state, is isolated from the effects of subsequent tests operating on it, and
does not rely on an inexplicit ordering or specific sequencing of tests. Keep
in mind, although Dr. Strangetest ensures your tests are run in an order to
satisfy declared dependencies, it does not otherwise guarantee that tests are
run in a particular order or sequence.


### Specifying Test Names

Prerequisite test names are specified as a string. For functions, this is just
the name of the function. Method names can be specified using the syntax
`classname::methodname`.

Since PHP treats dynamically-specified names as fully-qualified names, Dr.
Strangetest considers any qualified prerequisite name to be fully qualified and
attempts to resolve the test name as is. However, if provided with an
unqualified name, Dr. Strangetest applies its own name resolution.

If provided with an unqualified function name, Dr. Strangetest resolves the
name to either a method in the current class or a function in the current
namespace. You can force resolution to a function in the current namespace by
prepending the name with `::`, signifying an empty class. You can force
resolution to a function in the global namespace by prepending the name with
`\`.

If provided with an unqualifed class name, Dr. Strangetest resolves the name to
a class in the current namespace. You can force resolution to the global
namespace by prepending the name with `\`.

Here's an example of how Dr. Strangetest resolves prerequisite test names from
different contexts:

```php
<?php

namespace {
    function test_one(strangetest\Context $context)
    {
        $context->set('global function one');
    }

    function test_two(strangetest\Context $context)
    {
        $actual = $context->requires(
            'test_one',
            'Test::test_one',
            'example\test_one',
            'example\Test::test_one'
        );
        $expected = [
            'test_one' => 'global function one',
            'Test::test_one' => 'global method one',
            'example\test_one' => 'example function one',
            'example\Test::test_one' => 'example method one',
        ];
        assert($actual === $expected);
    }

    class Test
    {
        public function test_one(strangetest\Context $context)
        {
            $context->set('global method one');
        }

        public function test_two(strangetest\Context $context)
        {
            $actual = $context->requires(
                'test_one',
                '::test_one',
                'example\test_one',
                'example\Test::test_one'
            );
            $expected = [
                'test_one' => 'global method one',
                '::test_one' => 'global function one',
                'example\test_one' => 'example function one',
                'example\Test::test_one' => 'example method one',
            ];
            assert($actual === $expected);
        }
    }
}

namespace example {

    use strangetest;

    function test_one(strangetest\Context $context)
    {
        $context->set('example function one');
    }

    function test_two(strangetest\Context $context)
    {
        $actual = $context->requires(
            'test_one',
            'Test::test_one',
            '\test_one',
            '\Test::test_one'
        );
        $expected = [
            'test_one' => 'example function one',
            'Test::test_one' => 'example method one',
            '\test_one' => 'global function one',
            '\Test::test_one' => 'global method one',
        ];
        assert($actual === $expected);
    }

    class Test
    {
        public function test_one(strangetest\Context $context)
        {
            $context->set('example method one');
        }

        public function test_two(strangetest\Context $context)
        {
            $actual = $context->requires(
                'test_one',
                '::test_one',
                '\test_one',
                '\Test::test_one'
            );
            $expected = [
                'test_one' => 'example method one',
                '::test_one' => 'example function one',
                '\test_one' => 'global function one',
                '\Test::test_one' => 'global method one',
            ];
            assert($actual === $expected);
        }
    }
}
```

### Depending on Tests with Subtests

A test may declare a dependency on a test that uses [subtests](@#subtests). The
prerequisite is considered to have passed if all the prerequisite's subtests
pass. The prerequisite may [set a result](@#setting-a-test-result) as normal.


### Depending on Tests That Are Run Multiple Times

Dr. Strangetest's [test fixtures](@test-fixtures) make it possible to [run
tests multiple times](@test-fixtures#running-tests-multiple-times). Dependents
may themselves be run multiples times and may declare dependencies on
prerequisites that may also be run multiple times. How dependencies are
resolved depends on the relationship between the two tests.

By default, there is an implicit, top-level test run that comprises all the
tests in the test suite. If a test suite does not use any test run fixtures,
the entire test suite will consist of just this one test run. However, run
fixtures create "sub-runs" that are children of the top-level run: the tests
are part of the top-level run, but they are executed multiple times within it.
A sub-run may, in turn, have its own sub-runs. This forms a tree: every sub-run
is a child of exactly one parent run.

When a test is executed, it is executed within the context of a particular run.
If a test belongs to multiple runs, it is executed once for every run. Dr.
Strangetest remembers the outcome of every test execution as well as any result
the test may have saved and associates them with the appropriate run.

Given some test run, the tests that constitute the run are executed one or more
times (with multiple test executions implying the test belongs to sub-runs of
the current run). If all of a test's executions pass, the test passes the run,
otherwise it fails. If we're interested in the outcome of particular test but
the test is not part of the current run, we can move up the hierarchy until
finding a run that includes the test (potentially reaching the top-level run,
which includes every test).

When a dependent is executed, it will have some run in common with its
prerequisite: either the prerequisite is part of the same run, or the two tests
have a parent run in common. Dr. Strangetest finds this common run and uses the
prerequisite's outcome for that run to determine if the dependency is
satisfied. If this resolves to a single execution of the prerequisite and the
prerequisite saved a result, that result is provided to the dependent.
Otherwise, no test result is available.

This explanation may be conceptually difficult to grasp, so here is an example
that hopefully demonstrates this more clearly:

```php
<?php
// setup.php

function setup_run_dir1()
{
    return [1];
}

function setup_run_dir2()
{
    return [2];
}
```
```php
<?php
// test_a.php

namespace a;
use strangetest\Context;

function setup_run_a1(int $dir_arg)
{
    return [$dir_arg, 3];
}

function setup_run_a2(int $dir_arg)
{
    return [$dir_arg, 4];
}

function test_one(int $dir_arg, int $file_arg, Context $context)
{
    $context->set([$dir_arg, $file_arg]);
}

function test_two(int $dir_arg, int $file_arg, Context $context)
{
    $actual = $context->requires(
        'test_one',
        'b\test_one',
        'c\test_one'
    );
    $expected = [
        'test_one' => [$dir_arg, $file_arg],
        'c\test_one' => $dir_arg,
    ];
    assert($expected === $actual);
}
```
```php
<?php
// test_b.php

namespace b;
use strangetest\Context;

function setup_run_b1(int $dir_arg)
{
    return [$dir_arg, 5];
}

function setup_run_b2(int $dir_arg)
{
    return [$dir_arg, 6];
}

function test_one(int $dir_arg, int $file_arg, Context $context)
{
    assert((1 === $dir_arg) || (5 === $file_arg));
    $context->set([$dir_arg, $file_arg]);
}

function test_two(int $dir_arg, int $file_arg, Context $context)
{
    $actual = $context->requires(
        'test_one',
        'a\test_one',
        'c\test_one'
    );
    $expected = [
        'test_one' => [$dir_arg, $file_arg],
        'c\test_one' => $dir_arg,
    ];
    assert($expected === $actual);
}
```
```php
<?php
// test_c.php

namespace c;
use strangetest\Context;

function test_one(int $dir_arg, Context $context)
{
    $context->set($dir_arg);
}

function test_two(int $dir_arg, Context $context)
{
    $actual = $context->requires(
        'test_one',
        'a\test_one',
        'b\test_one'
    );
    $expected = ['test_one' => $dir_arg];
    assert($expected === $actual);
}
```

The tests in `test_a.php` will each be run four times, and their runs will be
`(dir1, a1)`, `(dir1, a2)`, `(dir2, a1)`, and `(dir2, a2)`.

Similarly, the tests in `test_b.php` will also each be run four times, but
their runs will be `(dir1, b1)`, `(dir1, b2)`, `(dir2, b1)`, and `(dir2, b2)`.

Meanwhile, the tests in `test_c.php` will each only be run twice, with their
runs being `(dir1)`, and `(dir2)`.

Consider the dependencies declared in `a\test_two`:

-   `a\test_one` is in the same run, so the dependency is determined by each
    run of `a\test_one`, which also means each test result saved by
    `a\test_one` is available to `a\test_two`. This is verified by asserting
    that the retrieved values are the same as those received by parameters
    `$dir_arg` and `$file_arg`.

-   `b\test_one` is not in the same run, but there is a common parent run:
    `a\test_two (dir1, a1)` and `a\test_two (dir1, a2)` depend on `b\test_one
    (dir1)`, while `a\test_two (dir2, a1)` and `a\test_two (dir2, a2)` depend
    on `b\test_one (dir2)`. In each case, the dependency is determined by two
    runs of `b\test_one`: `b\test_one (dir1)` is determined by the net result
    of `b\test_one (dir1, b1)` and `b\test_one (dir1, b2)`, while `b\test_one
    (dir2)` is determined by the net result of `b\test_one (dir2, b1)` and
    `b\test_one (dir2, b2)`. Consequently, no saved results are available to
    `a\test_two`.

-   `c\test_one` is also not in the same run, and like `b\test_one` has the
    same parent runs in common: `a\test_two (dir1, a1)` and `a\test_two (dir1,
    a2)` depend on `c\test_one (dir1)`, while `a\test_two (dir2, a1)` and
    `a\test_two (dir2, a2)` depend on `c\test_one (dir2)`. Unlike `b\test_one`,
    this time each dependency is determined by a single run of `c\test_one`,
    and so the test's saved results are available to `a\test_two`. This is
    verified by asserting that the retrieved values is the same as that
    received by the `$dir_arg` parameter.

From this, it is hopefully clear how the dependencies for `b\test_two` and
`c\test_two` are resolved.

Now consider the failure of test `b\test_one (dir2, b2)` when `$dir_arg` is `2`
and `$file_arg` is `6`:

-   `b\test_two (dir2, b2)` is skipped while the other three runs of
    `b\test_two` pass.

-   The failure of `b\test_one (dir2, b2)` causes the overall failure of
    `b\test_one (dir2)`, which causes `a\test_two (dir2, a1)`, `a\test_two
    (dir2, a2)` and `c\test_two (dir2)` to all be skipped.

We can verify all this by running Dr. Strangetest:

```shell
$ strangetest --verbose
Dr. Strangetest

.........FS.S....SS.


FAILED: b\test_one (dir2, b2)
assert(1 === $dir_arg || 5 === $file_arg)
in test_b.php:19



SKIPPED: b\test_two (dir2, b2)
This test depends on 'b\test_one (dir2, b2)', which did not pass
in test_b.php on line 28



SKIPPED: c\test_two (dir2)
This test depends on 'b\test_one (dir2)', which did not pass
in test_c.php on line 17



SKIPPED: a\test_two (dir2, a1)
This test depends on 'b\test_one (dir2)', which did not pass
in test_a.php on line 27



SKIPPED: a\test_two (dir2, a2)
This test depends on 'b\test_one (dir2)', which did not pass
in test_a.php on line 27



Seconds elapsed: 0.001
Memory used: 1.212 MB
Passed: 15, Failed: 1, Skipped: 4
```
