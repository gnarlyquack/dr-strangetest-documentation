# Test Fixtures

A test "fixture" is a controlled environment in which a system is tested, and
it includes initializing the system to a state suitable for testing. Setting
this up is usually repetitive drudgery and may often constitute the majority of
the work when writing your tests. It's therefore desirable to centralize this
work into one or more fixture setup functions. Tests that require the same
fixture can then be grouped together and use these common functions to
initialize their environment.

You may also need to clean up, or "teardown", your test fixture after testing.
Since PHP is garbage collected this is usually unnecessary, but if you're
working with external resources -- opening a file handle, setting a global
configuration variable, etc. -- you need to do some clean up.

Most of the time you want to recreate your test fixture from scratch for each
test. This is to ensure, as much as possible, the outcome of each test depends
only on its fixture and not on other tests or external phenomena, a concept
called "test isolation". In practice, creating an entirely new fixture for each
test isn't always possible or even, at times, desirable. In these cases, being
able to manage test fixture at different levels of "granularity" is useful so
that different fixture components can be reused among a common set of tests.


## Fixture Functions

Dr. Strangetest offers a number of functions to manage your test fixture. Just
write them into your test files and Dr. Strangetest will discover and use them
just as it does your tests. Setup functions are run before your tests and are
used to set up your test environment to a desired initial condition. Teardown
functions are run after your tests and perform any needed cleanup. Teardown
functions are run regardless of the outcome of a test, although if a setup
function throws an exception, its associated tests and corresponding teardown
function are skipped.

The functions described below are all discovered without regard to case.
Although function names are given in snake\_case, they're also recognized if
underscores are omitted. Many of the functions need only begin with the listed
name and may otherwise have arbitrary names, making the use of namespaces
optional. If conflicting setup and/or teardown names are ever found, an error
is reported and the associated tests are skipped.


### Test-Specific Teardown

Test-specific teardown allows an individual test function to register teardown
functions that will be run after the test completes. This is implemented
through the `strangetest\Context` interface, an instance of which is provided
as the last argument to every test function and test method. The interface
provides the following method:

```php
public function strangetest\Context::teardown(callable $callback): void
```

`$callback` is a callable that should take no parameters and return `void`.

Calling this method multiple times will register multiple teardown functions.

Upon completion of the test, each callback is run in the reverse order in which
it was registered, after which it is disposed of.


### Method Setup and Teardown

If a test class defines a public method named `setup`, that method is run
before every test method.

If a test class defines a public method named `teardown`, that method is run
after every test method.


### Object Setup and Teardown

If a test class defines a public method named `setup_object`, that method is
run after an object instance is instantiated and before any other method.

If a test class defines a public method named `teardown_object`, that method is
run after running all of the object's tests.


### Function Setup and Teardown

If a test file defines a function whose name begins with `setup` (and doesn't
also match other file function names given below), that function is run before
every test function.

If a test file defines a function whose name begins with `teardown` (and
doesn't match other file function names given below), that function is run
after every test function.


### File Setup and Teardown

If a test file defines a function whose name begins with `setup_file`, that
function is run before running any other function or instantiating any other
class in the file.

If a test file defines a function whose name begins with `teardown_file`, that
function is run after finishing all tests in the file.


### Directory Setup and Teardown

If a test directory contains a file named `setup.php`, it is the first file
included and it is searched for the fixture functions described below. The file
is **not** searched for test names. It is not required to define fixture
functions in this file, as the file may also be used to define (or include)
definitions needed by your test suite. Note that discovery is **not** performed
on any file included by `setup.php`.

If `setup.php` defines a function whose name begins with `setup`, that function
is run prior to running any tests in the directory (or subdirectories).

If `setup.php` defines a function whose name begins with `teardown`, that
function is run after completing all tests in the directory (as well as any
subdirectories) and prior to ascending out of the directory.


### Run Setup and Teardown

Run fixtures let you [run your tests multiple
times](@#running-tests-multiple-times), once for each run fixture. Run fixtures
may be defined at the file level and at the directory level. File-level
fixtures are defined directly in a test file and directory-level fixtures are
defined in a directory's `setup.php` file.

A run setup fixture is a function whose name begins with `setup_run`. Each
function defines a new test run, and the portion of the function name after the
`setup_run` prefix is used as the name of the run. A `setup_run` function may
have a matching `teardown_run` function, but run teardown functions cannot
exist on their own.

Test runs are executed in an arbitrary order. Each run begins by calling
`setup_run`, then executes any subordinate fixture functions and tests, and
then calls the matching `teardown_run` function (if there is one).


## Managing Resources

One of the most straightforward uses of fixture functions is to manage
resources that may persist beyond the lifetime of a test if not properly
cleaned up. Some typical examples include files created on the filesystem,
configuration of global settings and variables, and connections to external
services such as a database.

Another common example is a situation where you'd like to test a function's
output using PHP's output buffering:

```php
function test_output()
{
    ob_start();
    produce_output();
    assert('Expected output' === ob_get_contents());
    ob_end_clean();
}
```

If the assertion fails, the output buffer is never deleted. Even if you use
`ob_get_clean` to delete the buffer as you get its contents, this does not
guard against errors during the call to `produce_output`.

If this is the only test using an output buffer, we can ensure the buffer is
deleted by using a test-specific teardown function:

```php
function test_output(strangetest\Context $context)
{
    ob_start();
    $context->teardown('ob_end_clean');
    produce_output();
    assert('Expected output' === ob_get_contents());
}
```

If an output buffer is needed by multiple tests, we can move management of the
buffer into function fixture functions which are run before and after every
test function:

```php
function setup()
{
    ob_start();
}

function teardown()
{
    ob_end_clean();
}

function test_output()
{
    produce_output();
    assert('Expected output' === ob_get_contents());
}

function test_more_output()
{
    produce_more_output();
    assert('More expected output' === ob_get_contents());
}
```


## Providing State to Tests

Dr. Strangetest's fixture functions form a hierarchy with directories at the
top and individual tests at the bottom. Setup functions can provide state to
functions lower in the hierarchy by returning an array of items, which are
unpacked and provided as arguments to subordinate fixture functions, class
constructors, and test functions. These subordinate functions accept them by
adding parameters to their signature.

Subordinate setup functions "intercept" state from higher setup functions.
Whatever these subordinate functions return replaces whatever state is passed
to it. This is true regardless of whether or not a function explicitly accepts
the state provided to it. Functions may add to, remove from, alter or simply
pass through the state they receive. If a setup function is not defined at a
particular level in the hierarchy, state is passed directly to the next
subordinate setup function, test function or test class.

State is also passed to teardown functions, but these functions never return
state, they only clean up what is given to them. Teardown functions receive
either the state returned by their corresponding setup function, if there is
one, or the state returned by the next superior setup function.

Inside of a object, things work a little differently. Since an object's methods
all have access to their object's shared state, fixture methods can directly
initialize this state, which other test methods can then access. Consequently,
state is never explicitly passed around within an object. Objects can receive
external state in their constructor, which it can use to initialize the object.

Consider an example where a common database connection is shared among a
directory of tests:

```php
<?php declare(strict_types=1);
// setup.php

namespace test;

use example\Database;

function setup(): array
{
    $database = new Database();
    $database->createDatabase();
    return [$database];
}

function teardown(Database $database): void
{
    $database->deleteDatabase();
}
```

One of the directory's test files might have the following:


```php
<?php declare(strict_types=1);
// test.php

namespace test;
use example\Database;
use function strangetest\assert_identical;

class TestDatabase
{
    private Database $database;

    public function __construct(Database $database)
    {
        $this->database = $database;
    }

    public function setup(): void
    {
        $this->database->reset();
    }

    public function testInsertRecord(): void
    {
        $this->database->insertRecord([1, 2]);
        assert_identical([[1, 2]], $this->database->records());
    }

    public function testDeleteRecord(): void
    {
        $id = $this->database->insertRecord([1, 2]);
        assert_identical([[1, 2]], $this->database->records());

        $this->database->deleteRecord($id);
        assert_identical([], $this->database->records());
    }
}

```

In the above example, since there is no file setup function, the state returned
from `test\setup` is provided directly to `test\TestDatabase`. Once passed to a
constructor, the state becomes available from within the object as part of the
object's shared state. Consequently, fixture methods never return or receive
state. However, you could also write your test using functions:

```php
<?php declare(strict_types=1);
// test.php

namespace test\database;

use example\Database;
use function strangetest\assert_identical;

function setup(Database $database): array
{
    $database->reset();
    return [$database];
}

function test_insert_record(Database $database): void
{
    $database->insertRecord([1, 2]);
    assert_identical([[1, 2]], $database->records());
}

function test_delete_record(Database $database): void
{
    $id = $database->insertRecord([1, 2]);
    assert_identical([[1, 2]], $database->records());

    $database->deleteRecord($id);
    assert_identical([], $database->records());
}
```

In this case, the state returned from `test\setup` is provided to
`test\database\setup`, which then returns state that is provided to each test.
If more setup or teardown is needed, you can add the necessary functions and
state is automatically provided to them.

```php
<?php declare(strict_types=1);
// test.php

namespace test\database;

use example\Database;
use function strangetest\assert_identical;

function setup_file(Database $database): array
{
    $database->loadTestData();
    return [$database];
}

function teardown_file(Database $database): void
{
    $database->clearTestData();
}

function setup(Database $database): array
{
    $database->reset();
    return [$database];
}

function test_insert_record(Database $database): void
{
    $database->insertRecord([1, 2]);
    assert_identical([[1, 2]], $database->records());
}

function test_delete_record(Database $database): void
{
    $id = $database->insertRecord([1, 2]);
    assert_identical([[1, 2]], $database->records());

    $database->deleteRecord($id);
    assert_identical([], $database->records());
}
```

You can do the same thing if you organized your tests in a class, but in this
case you might replace the file fixture functions with object fixture methods:

```php
<?php declare(strict_types=1);
// test.php

namespace test;
use example\Database;
use function strangetest\assert_identical;

class TestDatabase
{
    private Database $database;

    public function __construct(Database $database)
    {
        $this->database = $database;
    }

    public function setupObject(): void
    {
        $this->database->loadTestData();
    }

    public function teardownObject(): void
    {
        $this->database->clearTestData();
    }

    public function setup(): void
    {
        $this->database->reset();
    }

    public function testInsertRecord(): void
    {
        $this->database->insertRecord([1, 2]);
        assert_identical([[1, 2]], $this->database->records());
    }

    public function testDeleteRecord(): void
    {
        $id = $this->database->insertRecord([1, 2]);
        assert_identical([[1, 2]], $this->database->records());

        $this->database->deleteRecord($id);
        assert_identical([], $this->database->records());
    }
}
```

The state returned by a setup function replaces whatever state may have existed
before it. If you define a setup function, it **MUST** accept and pass on the
arguments it receives if those arguments are needed at lower levels.

Expanding on the database example:

```php
<?php declare(strict_types=1);
// test_orders.php

namespace test\orders;

use example\Database;
use example\OrderManager;
use example\PaymentProcessor;
use function strangetest\assert_true;

function setup_file(): array
{
    $processor = new PaymentProcessor();
    $processor->setTestMode();
    return [$processor];
}

function setup(Database $database, PaymentProcessor $processor): array
{
    return [new OrderManager($database, $processor)];
}

function test(OrderManager $order): void
{
    $order->placeOrder();
    assert_true($order->wasPlaced());
}
```

The above example results in an error because `test\orders\setup_file` removes
the `Database` argument provided by `test\setup`, which is needed by
`test\orders\setup`. A fixed example:

```php
<?php declare(strict_types=1);
// test_orders.php

namespace test\orders;

use example\Database;
use example\OrderManager;
use example\PaymentProcessor;
use function strangetest\assert_true;

function setup_file(Database $database): array
{
    $database->loadTestData();

    $processor = new PaymentProcessor();
    $processor->setTestMode();

    return [$database, $processor];
}

function teardown_file(Database $database, PaymentProcessor $_): void
{
    $database->clearTestData();
}

function setup(Database $database, PaymentProcessor $processor): array
{
    $database->reset();
    return [new OrderManager($database, $processor)];
}

function test(OrderManager $order): void
{
    $order->placeOrder();
    assert_true($order->wasPlaced());
}
```


## Running Tests Multiple Times

[Run fixture functions](@#run-setup-and-teardown) let you take advantage of
[test parameterization](@#providing-state-to-tests) and run your tests multiple
times with varying parameters. This might be useful if you have multiple
implementations of a service and you want to ensure client code behaves
identically regardless of the service implementation that's used. Run fixture
functions may be used in a directory's `setup.php` to run all tests in that
directory multiple times, or within a test file to run all tests in that file
multiple times.

Run setup functions are functions whose name begins with `setup_run_`. The
remainder of the function name is used to name the test run, which is used in
the test report when displaying outcomes specific to the run. For example,
given a run setup function named `setup_run_foo`, a test that fails the run
will be identified in the test report as:

    FAILED: test (foo)

If Dr. Strangetest is unable to determine a unique run name from a run setup
function, an error is reported and the run is skipped.

Like other setup fixtures, run setup functions are provided with the current
test state. Unlike other setup fixtures, run setup functions **MUST** return
state. Since the whole point of run fixtures is to exercise your tests multiple
times with varying arguments, each run fixture must provide arguments to use in
your tests.

Run teardown functions can also be defined, but they cannot exist on their own,
they must be defined in conjunction with a run setup function. Run teardown
functions are functions whose name begins with `teardown_run_`. The remainder
of the function name must match a run name defined by a run setup function. The
run teardown function is passed whatever state is returned by its corresponding
setup function.

Continuing with the previous example, assume there are multiple database and
payment processor backends that we want to support, and we want to ensure
behavior is the same regardless of the backends being used. With run fixture
functions, we can run our tests with every combination of database and payment
processor.

```php
<?php declare(strict_types=1);
// setup.php

namespace test;

use example\Database;
use example\DatabaseX;
use example\DatabaseY;

function setup_run_database_x(): array
{
    $database = new DatabaseX();
    return [$database];
}

function setup_run_database_y(): array
{
    $database = new DatabaseY();
    return [$database];
}

function setup(Database $database): array
{
    $database->createDatabase();
    return [$database];
}

function teardown(Database $database): void
{
    $database->deleteDatabase();
}
```

```php
<?php declare(strict_types=1);
// test_orders.php

namespace test\orders;

use example\Database;
use example\OrderManager;
use example\PaymentProcessor;
use example\PaymentProcessorA;
use example\PaymentProcessorB;
use function strangetest\assert_true;

function setup_run_processor_a(Database $database): array
{
    $processor = new PaymentProcessorA();
    return [$database, $processor];
}

function setup_run_processor_b(Database $database): array
{
    $processor = new PaymentProcessorB();
    return [$database, $processor];
}

function setup_file(Database $database, PaymentProcessor $processor): array
{
    $database->loadTestData();
    $processor->setTestMode();
    return [$database, $processor];
}

function teardown_file(Database $database, PaymentProcessor $_): void
{
    $database->clearTestData();
}

function setup(Database $database, PaymentProcessor $processor): array
{
    $database->reset();
    return [new OrderManager($database, $processor)];
}

function test(OrderManager $order): void
{
    $order->placeOrder();
    assert_true($order->wasPlaced(), 'Order was not placed');
}
```

If any of the runs fail, it will be identified in the test report.

```
$ strangetest
Dr. Strangetest

.F..


FAILED: test\orders\test (database_x, processor_b)
Assertion "$actual === true" failed
Order was not placed

$actual = false

in tests/test_orders.php on line 47



Seconds elapsed: 0.001
Memory used: 1.212 MB
Passed: 3, Failed: 1
```
