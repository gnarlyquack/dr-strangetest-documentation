# Writing Tests

## What is a Test?

EasyTest automatically discovers your tests using the following rules:

- A **test** is a function or method whose name begins with `test`. When such
  a function or method is found, it is run.
- Test methods are organized into test classes, which is any class whose name
  begins with `test`. When such a class is found, an instance of it is
  instantiated and it is searched for test methods.
- Test functions and test classes are organized into test files, which is any
  PHP source file whose name begins with `test` and has file extension `.php`.
  When such a file is found, it is included and searched for test functions
  and test classes. A test file may contain any combination of test functions
  and/or test classes.
- Test files may be organized into test directories, which is any directory
  whose name begins with `test`. When such a directory is found, it is
  searched for test files and also for subdirectories whose name also begins
  with `test`.
- Names are discovered without regard to case.

Knowing this, you could put your tests in individual files right in your
source directory, but it's recommended to instead keep them organized in a
subdirectory named `tests`. After several iterations, you might end up with
the following:

```php
<?php
// tests/test_hello.php

use function easytest\assert_identical;
use example\greet\Hello;

function test_hello_to_the_world() {
    $hello = new Hello;
    assert_identical('Hello, world!', $hello->greet());
}

function test_hello_to_humans() {
    $hello = new Hello;
    assert_identical('Hello, human!', $hello->greet('human'));
}
```

```php
<?php
// tests/test_goodbye.php

use function easytest\assert_identical;
use example\greet\GoodBye;

function test_goodbye_to_the_world() {
    $adieu = new GoodBye;
    assert_identical('Goodbye, cruel world!', $adieu->bid());
}

function test_goodbye_to_humans() {
    $adieu = new GoodBye;
    assert_identical('Goodbye, human!', $adieu->bid('human'));
}
```

Assuming you have written the code to make these tests pass, running your
tests looks something like:

    $ easytest

    ....


    Seconds elapsed: 0.002
    Passed: 4

Alternatively, you might want to consolidate these tests into one file since
they're testing the same `greet` module:

```php
<?php
// tests/test_greet.php

use function easytest\assert_identical;
use example\greet\GoodBye;
use example\greet\Hello;

class TestHello {
    public function TestHelloToTheWorld() {
        $hello = new Hello;
        assert_identical('Hello, world!', $hello->greet());
    }

    public function TestHelloToHumans() {
        $hello = new Hello;
        assert_identical('Hello, human!', $hello->greet('human'));
    }
}

class TestGoodBye {
    function TestGoodByeToTheWorld() {
        $adieu = new GoodBye;
        assert_identical('Goodbye, cruel world!', $adieu->bid());
    }

    function TestGoodByeToHumans() {
        $adieu = new GoodBye;
        assert_identical('Goodbye, human!', $adieu->bid('human'));
    }
}
```

And checking with EasyTest:

    $ easytest

    ....


    Seconds elapsed: 0
    Passed: 4

EasyTest endeavors to let you write your tests whichever way is most natural
to you.


## Making Assertions

A test "passes" unless an assertion fails or an error happens. Failures and
errors are signalled by throwing an exception. This means a test typically
ends immediately when a failure or an error happens.

Although prior examples use assertions provided by EasyTest, you could use
PHP's `assert`:

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
no means comprehensive. PHP's `assert` is available so you can make any
assertion you need (although you can always [write your
own](@writing-assertions)).

A full list of EasyTest's assertions is listed in the
[README](https://github.com/gnarlyquack/easytest).


## Testing Exceptions and Errors

Although nothing stops you from using `try` and `catch` to test for
exceptions, EasyTest provides `easytest\assert_throws` to (hopefully)
simplify the process. The function takes the name of an expected exception as
well as a callable and fails if invoking the callable doesn't result in the
expected exception being thrown. Otherwise it returns the exception instance.

```php
function test_exception() {
    $actual = easytest\assert_throws(
        ErrorException::class,
        function() {
            return 3 / 0;
        }
    );
    easytest\assert_identical(
        'Division by zero', $actual->getMessage()
    );
}
```

You might note that dividing by zero actually triggers a warning (as of PHP
7.4), not an exception. As you can see, EasyTest converts any (non-fatal)
error into an `ErrorException` and throws it.


## Skipping Tests

Your test suite might want to skip tests if it determines those tests are
incapable of being run, e.g., a version requirement isn't met or an extension
isn't enabled. For this, use `easytest\skip`, which takes a string explaining
why the test is being skipped.

```php
function test_skip() {
    if (version_compare(PHP_VERSION, MAX_VERSION) >= 0) {
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
normally give any details. Since you will likely be running the test suite
repeatedly, showing details about expected skipped tests usually just clutters
the report. Follow the provided suggestion to see what tests were skipped:

    $ easytest --verbose

    ........S.


    SKIPPED: test_skip
    PHP version must be less than 7.2
    in tests/test_skip.php on line 5



    Seconds elapsed: 0.003
    Passed: 9, Skipped: 1


## Subtests

While building out your greet module, you've decided you want a different
greeting based on the time of day. You might be tempted to write:

```php
function test_greetings() {
    $greetings = [
        [new MorningGreeting, 'Good morning, world!'],
        [new AfternoonGreeting, 'Good afternoon, world!'],
        [new EveningGreeting, 'Good evening, world!'],
        [new NightGreeting, 'Good night, world!'],
    ];

    foreach ($greetings as [$greeter, $expected]) {
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

Subtests ensure a test continues even if an assertion fails. EasyTest
implements this by providing every test function and test method an instance
of `easytest\Context`. This is always passed as the last parameter. The
`Context` object mirrors EasyTest's exceptions but returns `true` or `false`
indicating if the assertion passed instead of throwing an exception.

```php
function test_greetings(easytest\Context $context) {
    $greetings = [
        [new MorningGreet, 'Good morning, world!'],
        [new AfternoonGreet, 'Good afternoon, world!'],
        [new EveningGreet, 'Good evening, world!'],
        [new NightGreet, 'Good night, world!'],
    ];

    foreach ($greetings as [$greeter, $expected]) {
        $context->assert_identical($expected, $greeter->greet());
    }
}
```

Now you can see all failures:

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


## Test Dependencies

Test dependencies allow a test (the "dependent") to require one or more other
tests ("requisites") to first pass before the dependent is executed. If any
requisites are not successful, the dependent is skipped.

EasyTest implements this by providing every test function and test method an
instance of `easytest\Context`. This is always passed as the last parameter.
The `Context` object provides a `set` method for requisites to set state for
use by dependents and a `depend_on` method for dependents to declare their
dependency on requisites and retrieve any state saved by them.

```php
<?php

namespace test_stack;

use function easytest\assert_identical;
use easytest\Context;

function test_empty(Context $context) {
    $array = [];
    assert_identical([], $array);
    $context->set($array);
}

function test_push(Context $context) {
    $array = $context->depend_on('test_empty');
    array_push($array, 'foo');
    assert_identical(['foo'], $array);
    $context->set($array);
}

function test_pop(Context $context) {
    $array = $context->depend_on('test_push');
    assert_identical('foo', array_pop($array));
    assert_identical([], $array);
}
```

A dependent can declare a dependency on multiple requisites by passing
multiple names to `depend_on`. In this case, an associative array of the
state saved by the requisites is returned indexed by the provided names. Note
that there is no requirement for a requisite to save state, and if it did not,
it is not included in the array.

```php
<?php

namespace multiple_dependencies;

use function easytest\assert_identical;
use easytest\Context;

function test_one(Context $context) {
    $context->set(1);
}

function test_two() {
}

function test_three(Context $context) {
    $context->set(3);
}

function test_four(Context $context) {
    $state = $context->depend_on('test_one', 'test_two', 'test_three');
    assert_identical(['test_one' => 1, 'test_three' => 3], $state);
}
```

You may have noticed that `depend_on` determines a fully-qualified name based
on the current context. In the previous examples, `depend_on` resolved the
function names to the correct namespaced functions even though the names are
not fully qualified. This also works in classes:

```php
<?php

use function easytest\assert_identical;
use easytest\Context;

class TestStack {
    public function testEmpty(Context $context) {
        $array = [];
        assert_identical([], $array);
        $context->set($array);
    }

    public function testPush(Context $context) {
        $array = $context->depend_on('testEmpty');
        array_push($array, 'foo');
        assert_identical(['foo'], $array);
        $context->set($array);
    }

    public function testPop(Context $context) {
        $array = $context->depend_on('testPush');
        assert_identical('foo', array_pop($array));
        assert_identical([], $array);
    }
}
```

You can, of course, always provide a fully-qualified name to depend on a
function or method in another namespace. Note that, if wanting to depend on a
name in the global namespace from a namespaced function or method, the name
**must** start with a backslash (`\`).  You can depend on a method from a
different class using the notation `ClassName::methodName`. As a convenience,
a method can depend on a function in the current namespace using the notation
`::function_name`.

[Multiple test
execution](@test-fixtures#multiple-parameterized-test-execution)
has not been discussed yet, but `depend_on` also assumes a requisite is run
with the same argument set as the dependent. A non-multiply-executed dependent
that depends on a multiply-executed requisite will only be run if all runs of
the requisite pass. A multiply-executed dependent can depend on a
non-multiply-executed requisite by using empty parenthesis after the name:
`requisite_name()`. Otherwise, a dependent can specify an argument set by
enclosing the name of the argument set in parenthesis after the name of the
requisite: `requisite_name(argument_set_name)`.
