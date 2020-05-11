- [Getting Started](#getting-started)
- [Test Discovery](#test-discovery)
- [Making Assertions](#making-assertions)
- [Testing Exceptions and Errors](#testing-exceptions-and-errors)
- [Output](#output)
- [Skipping Tests](#skipping-tests)
- [Subtests](#subtests)


# Getting Started

Use Composer to add EasyTest to your project:

    composer require --dev easytest/easytest

This installs the EasyTest executable at `vendor/bin/easytest`, although from
hereon, we're just going to refer to the executable as `easytest` instead of
referring to the whole path.


# Test Discovery

Run EasyTest on the command line from your project's root source directory. It
searches the directory for tests and runs any it finds.

    $ easytest

    No tests found!

Fair enough. Let's add some.

EasyTest operates as follows:

- A **test** is a function or method whose name begins with `test`. When such
  a function or method is found, it is run.
- Test methods are organized into test classes, which is any class whose name
  begins with `test`. When such a class is found, an instance of it is
  instantiated and it is searched for test methods.
- Test functions and test classes are organized into test files, which is any
  PHP source file whose name begins with `test` (and has file extension
  `.php`). When such a file is found, it is included and searched for test
  functions and test classes. A test file may contain any combination of test
  functions and/or test classes.
- Test files may be organized into test directories, which is any directory
  whose name begins with `test`. When such a directory is found, it is
  searched for test files and also for subdirectories whose name also begins
  with `test`.

Names are matched without regards to case.

EasyTest also loads Composer's autoloader so our project is automatically
visible to our tests.

Knowing this, we could put our tests in individual files right in our source
directory. But let's instead keep them organized in a subdirectory named
`tests`. After several iterations, we might end up with the following files:

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
// tests/test_goodbye.php

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

To be honest, these files are looking pretty thin, and since they both test
the same module "greet", we might decide to consolidate them:

```php
<?php
// tests/test_greet.php

use example\greet\GoodBye;
use example\greet\Hello;


class TestHello {
    public function TestHelloToTheWorld() {
        $hello = new Hello;
        easytest\assert_identical('Hello, world!', $hello->greet());
    }

    public function TestHelloToHumans() {
        $hello = new Hello;
        easytest\assert_identical('Hello, human!', $hello->greet('human'));
    }
}


class TestGoodBye {
    function TestGoodByeToTheWorld() {
        $adieu = new GoodBye;
        easytest\assert_identical('Goodbye, cruel world!', $adieu->bid());
    }

    function TestGoodByeToHumans() {
        $adieu = new GoodBye;
        easytest\assert_identical('Goodbye, human!', $adieu->bid('human'));
    }
}
```

And checking with EasyTest:

    $ easytest

    ....


    Seconds elapsed: 0.002
    Passed: 4


# Making Assertions

A test "passes" unless an assertion fails or some other error happens.
Failures and errors are signalled by the throwing of an exception. This means
a test typically ends immediately when a failure or an error happens.

Although prior examples use assertions provided by EasyTest, we could use
PHP's `assert()`:

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
assertion you need (although you can always [write your
own](https://github.com/gnarlyquack/easytest/wiki/Writing-Assertions)).

A full list of EasyTest's assertions is listed in the
[README](https://github.com/gnarlyquack/easytest).

# Testing Exceptions and Errors

Although nothing stops you from using `try` and `catch` to test for
exceptions, EasyTest provides `easytest\assert_throws()` to (hopefully)
simplify the process. The function takes the name of an expected exception as
well as a callable and fails if invoking the callable doesn't result in the
expected exception being thrown. Otherwise it returns the exception instance.

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


# Output

Use PHP's output buffers to test output:

```php
function test_buffering() {
    ob_start();
    function_that_produces_output();
    easytest\assert_identical('Expected output', ob_get_contents());
    ob_end_clean();
}
```

Although this example works, it is flawed: if the assertion fails, the output
buffer is never deleted, and EasyTest reports an error (in addition to the
failure) if we start an output buffer and never delete it. Even if we use
`ob_get_clean()` to delete the buffer as we get its contents, the function
under test might generate an error and the assertion may never be reached. To
remedy this, we can use [fixture
functions](https://github.com/gnarlyquack/easytest/wiki/Test-Fixtures) to
ensure the output buffer is always deleted after a test.

EasyTest also buffers our tests to capture and report any output we don't
handle during the test run. Although EasyTest indicates when output occurs, it
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


# Skipping Tests

Your test suite might want to skip tests if it determines those tests are
incapable of being run, e.g., a version requirement might not be met or an
extension might not be enabled. For this, use `easytest\skip()`, which takes a
string explaining why the test is being skipped.

```php
function test_skip() {
    if (!version_compare(PHP_VERSION, MAX_VERSION, '<')) {
        easytest\skip('PHP version must be less than ' . MAX_VERSION);
    }

    // The actual test goes here. This is never reached if the version
    // requirement isn't met.
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


# Subtests

While building out our greet module, we've decided we want a different
greeting based on the time of day. We might be tempted to write:

```php
function test_greetings() {
    $greetings = [
        [new MorningGreeting, 'Good morning, world!'],
        [new AfternoonGreeting, 'Good afternoon, world!'],
        [new EveningGreeting, 'Good evening, world!'],
        [new NightGreeting, 'Good night, world!'],
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

Subtests ensure our test continues even if an assertion fails. EasyTest
implements this by providing every test function and test method an instance
of `easytest\Context`. This is always passed as the last parameter.

```php
function test_greetings(easytest\Context $context) {
    $greetings = [
        [new MorningGreeting, 'Good morning, world!'],
        [new AfternoonGreeting, 'Good afternoon, world!'],
        [new EveningGreeting, 'Good evening, world!'],
        [new NightGreeting, 'Good night, world!'],
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
provides methods with signatures identical to each of EasyTest's assertions,
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

Now we see all failures:

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
