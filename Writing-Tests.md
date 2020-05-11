# Writing Tests

- [Getting Started](#getting-started)
- [The Basics](#the-basics)
- [Testing Exceptions and Errors](#testing-exceptions-and-errors)
- [Output](#output)
- [Skipping Tests](#skipping-tests)
- [Subtests](#subtests)


## Getting Started

Use Composer to add EasyTest to your project:

    composer require --dev easytest/easytest

This installs the EasyTest executable at `vendor/bin/easytest`, although from
hereon, we're just going to refer to the executable as `easytest` instead of
referring to the whole path.


## The Basics

Run EasyTest on the command line from your project's root source directory. It
will search your directory for any tests and run them.

    $ easytest

    No tests found!

Fair enough. Let's add some.

Although we could put our tests in individual files right in our source
directory, we should probably keep them organized together. So instead let's
create a directory in our source directory named `tests`, inside of which we
might have (after several iterations) the following files:

```php
<?php
// tests/test_hello.php

use example\greet\Hello;

function test_hello_to_the_world() {
    $hello = new Hello;
    easytest\assert_identical('Hello, world!', $hello->greet());
}

function test_hello_to_humans() {
    $hello = new Hello;
    easytest\assert_identical('Hello, human!', $hello->greet('human'));
}
```

```php
<?php
// test_goodbye.php

use example\greet\GoodBye;

function test_goodbye_to_the_world() {
    $adieu = new GoodBye;
    easytest\assert_identical('Goodbye, cruel world!', $adieu->bid());
}

function test_goodbye_to_humans() {
    $adieu = new GoodBye;
    easytest\assert_identical('Goodbye, human!', $adieu->bid('human'));
}
```

Assuming we have written the code to make these tests pass, running our tests
looks something like:

    $ easytest

    ....


    Seconds elapsed: 0.002
    Passed: 4

Note the pattern: Any directory whose name begins with `test` is searched for
files and subdirectories whose name also begins with `test`. Any file whose
name begins with `test` is searched for functions whose name begins with
`test`. Any function whose name begins with `test` is run. EasyTest also loads
Composer's autoloader on start-up so our project is visible to our tests.

Right now, each test creates either its own Hello or GoodBye. We could extract
this code into its own functions and centralize our test setup:

```php
<?php
// tests/test_hello.php

namespace hellos;

use easytest;
use example\greet\Hello;

function setup_function() {
    return [new Hello];
}

function test_hello_to_the_world(Hello $hello) {
    easytest\assert_identical('Hello, world!', $hello->greet());
}

function test_hello_to_humans(Hello $hello) {
    easytest\assert_identical('Hello, human!', $hello->greet('human'));
}
```

```php
<?php
// test_goodbye.php

namespace goodbyes;

use easytest;
use example\greet\GoodBye;

function setup_function() {
    return [new GoodBye];
}

function test_goodbye_to_the_world(GoodBye $adieu) {
    easytest\assert_identical('Goodbye, cruel world!', $adieu->bid());
}

function test_goodbye_to_humans(GoodBye $adieu) {
    easytest\assert_identical('Goodbye, human!', $adieu->bid('human'));
}
```

`setup_function()` is run before each of our test functions and can return
arguments needed by our tests. EasyTest unpacks these arguments and uses them
to call our test functions. This is why the return parameter is an array:
although in this case our tests only take one parameter, other tests might
require multiple parameters.

We can also define a corresponding `teardown_function()` that is run after
each test. It too is passed the arguments from `setup_function()` so they can
be cleaned up as necessary.

We added namespaces to the test files to prevent a fatal error due to
duplicate definitions of `setup_function()`. Alternatively, we could give the
functions different names. EasyTest recognizes them as long as the name starts
with `setup_function`. For example, we could have named our setup functions
`setup_function_to_test_hello` and `setup_function_to_test_goodbye`. Teardown
functions work the same way.

Since these files are looking pretty thin, and since they both test the same
greet module, we might decide to consolidate them:

```php
<?php
// tests/test_greet.php

use example\greet\GoodBye;
use example\greet\Hello;


class TestHello {
    private $hello;

    public function SetUp() {
        $this->hello = new Hello;
    }

    public function TestHelloToTheWorld() {
        easytest\assert_identical('Hello, world!', $this->hello->greet());
    }

    public function TestHelloToHumans() {
        easytest\assert_identical('Hello, human!', $this->hello->greet('human'));
    }
}


class TestGoodBye {
    private $adieu;

    public function SetUp() {
        $this->adieu = new GoodBye;
    }

    function TestGoodByeToTheWorld() {
        easytest\assert_identical('Goodbye, cruel world!', $this->adieu->bid());
    }

    function TestGoodByeToHumans() {
        easytest\assert_identical('Goodbye, human!', $this->adieu->bid('human'));
    }
}
```

The pattern we noted before also applies to classes: within a test file, any
class whose name begins with `test` is instantiated, and any of its public
methods whose name begins with `test` are run. Classes can define public
methods named `setup()` and `teardown()` to setup and teardown its tests.
Unlike `setup_function()` and `teardown_function()`, they don't pass or
receive arguments as all methods have access to their object's shared state.

A test file may contain any combination of test functions and test classes.

You may have noticed something in the previous example: EasyTest matches all
names without regards to case, and it matches on both CamelCase and
snake_case. So we could have written our function-based test files like:

```php
<?php
// tests/test_hello.php

namespace hellos;

use easytest;
use example\greet\Hello;

function setupFunction() {
    return [new Hello];
}

function testHelloToTheWorld(Hello $hello) {
    easytest\assert_identical('Hello, world!', $hello->greet());
}

function testHelloToHumans(Hello $hello) {
    easytest\assert_identical('Hello, human!', $hello->greet('human'));
}
```

So far our tests have only used assertions provided by EasyTest, but we could
also use PHP's `assert()`:

```php
function testHelloToTheWorld() {
    $hello = new Hello;
    $expected = 'Hello, world!';
    $actual = $hello->greet();
    assert(
        $expected === $actual,
        "Unexpected hello\nexpected: $expected\nactual: $actual"
    );
}
```

Although you may find EasyTest's assertions easier to work with, they are by
no means comprehensive. PHP's `assert()` is available so you can make any
assertion you need.

This is probably most of what you'll need for the majority of your tests. For
a full list of EasyTest's features, including a list of its assertions, please
review EasyTest's [README](https://github.com/gnarlyquack/easytest).


## Testing Exceptions and Errors

`easytest\assert_throws()` takes the name of an expected exception as well as
a callable and fails if invoking the callable doesn't result in the expected
exception being thrown. Otherwise it returns the exception instance.

```php
function test_exception() {
    $actual = easytest\assert_throws(
        'ErrorException',
        function() {
            return 3 / 0;
        }
    );
    easytest\assert_identical(
        'Division by zero', $actual->getMessage()
    );
}
```

Dividing by zero actually triggers a warning (as of PHP 7.4), not an
exception. EasyTest converts any (non-fatal) error into an `ErrorException`
and throws it.


## Output

Use PHP's output buffers to test output:

```php
function setup_function() {
    ob_start();
}

function teardown_function() {
    ob_end_clean();
}

function test_output() {
    function_that_emits_output();
    easytest\assert_identical('Expected output', ob_get_contents());
}
```

We use a teardown function here to ensure the buffer is deleted whether our
test passed or failed. EasyTest reports an error if you start an output buffer
and don't delete it.

EasyTest also buffers our tests to capture and report any output that we don't
handle during our test run. Although EasyTest indicates output occurred, it
doesn't display it unless it occurred in a test that fails or has an error.

    $ easytest

    ..O.........


    This report omitted output.
    To view, rerun easytest with the --verbose option.

    Seconds elapsed: 0.003
    Passed: 11, Output: 1

We can follow the provided suggestion to see the output:

    $ easytest --verbose

    ..O.........


    OUTPUT: test_output
    Can you see me?



    Seconds elapsed: 0.003
    Passed: 11, Output: 1


## Skipping Tests

Your test suite might want to skip tests if it determines those tests are
incapable of being run, e.g., a version requirement might not be met or an
extension might not be enabled.

```php
function test_skip() {
    if (!version_compare(PHP_VERSION, MAX_VERSION, '<')) {
        easytest\skip('PHP version must be less than ' . MAX_VERSION);
    }

    // run test
}
```

The resulting test run might look something like:

    $ easytest

    ........S.


    This report omitted skipped tests.
    To view, rerun easytest with the --verbose option.

    Seconds elapsed: 0.003
    Passed: 9, Skipped: 1

Although EasyTest indicates tests were skipped during the test run, it doesn't
normally give us any details. Since we will likely be running the test suite
repeatedly, we do not want our report cluttered with expected skipped tests.
We can follow the provided suggestion to see what tests were skipped:

    $ easytest --verbose

    ........S.


    SKIPPED: test_skip
    PHP version must be less than 7.2
    in tests/test_skip.php on line 5



    Seconds elapsed: 0.003
    Passed: 9, Skipped: 1


## Subtests

While building out our greet module, we've decided we want a different
greeting based on the time of day. We might be tempted to write:

```php
function test_greetings() {
    $greetings = [
        [new MorningGreet, 'Good morning, world!'],
        [new AfternoonGreet, 'Good afternoon, world!'],
        [new EveningGreet, 'Good evening, world!'],
        [new NightGreet, 'Good night, world!'],
    ];

    foreach ($greetings as $greeting) {
        [$greeter, $expected] = $greeting;
        easytest\assert_identical($expected, $greeter->greet());
    }
}
```

The problem is, if any test fails, the next test isn't run.

    $ easytest

    F


    FAILED: test_greetings
    Assertion "$expected === $actual" failed

    - $expected
    + $actual

    - 'Good morning, world!'
    + 'Hello, world!'

    in tests/test_greetings.php on line 15



    Seconds elapsed: 0.002
    Failed: 1

Subtests ensure our assertions are run even if one fails. EasyTest
implements this by passing every test function and method an instance of
`easytest\Context`. This is always passed as the last parameter.

```php
function test_greetings(easytest\Context $context) {
    $greetings = [
        [new MorningGreet, 'Good morning, world!'],
        [new AfternoonGreet, 'Good afternoon, world!'],
        [new EveningGreet, 'Good evening, world!'],
        [new NightGreet, 'Good night, world!'],
    ];

    foreach ($greetings as $greeting) {
        [$greeter, $expected] = $greeting;
        $context->subtest(
            function() use ($greeter, $expected) {
                easytest\assert_identical($expected, $greeter->greet());
            }
        );
    }
}
```

Actually, we can make our test more straightforward. `easytest\Context`
provides methods with a signature identical to each of EasyTest's assertions,
except they behave as if they were run inside `easytest\Context::subtest()`,
i.e., your test continues even if they fail.

```php
function test_greetings(easytest\Context $context) {
    $greetings = [
        [new MorningGreet, 'Good morning, world!'],
        [new AfternoonGreet, 'Good afternoon, world!'],
        [new EveningGreet, 'Good evening, world!'],
        [new NightGreet, 'Good night, world!'],
    ];

    foreach ($greetings as $greeting) {
        [$greeter, $expected] = $greeting;
        $context->assert_identical($expected, $greeter->greet());
    }
}
```

Now we will see all failures:

    $ easytest

    FFFF


    FAILED: test_greetings
    Assertion "$expected === $actual" failed

    - $expected
    + $actual

    - 'Good morning, world!'
    + 'Hello, world!'

    in tests/test_greetings.php on line 15



    FAILED: test_greetings
    Assertion "$expected === $actual" failed

    - $expected
    + $actual

    - 'Good afternoon, world!'
    + 'Hello, world!'

    in tests/test_greetings.php on line 15



    FAILED: test_greetings
    Assertion "$expected === $actual" failed

    - $expected
    + $actual

    - 'Good evening, world!'
    + 'Hello, world!'

    in tests/test_greetings.php on line 15



    FAILED: test_greetings
    Assertion "$expected === $actual" failed

    - $expected
    + $actual

    - 'Good night, world!'
    + 'Hello, world!'

    in tests/test_greetings.php on line 15



    Seconds elapsed: 0.002
    Failed: 4
