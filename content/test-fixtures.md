# Test Fixtures

A test's "fixture" is the initial state of the system under test. Setting this
up is usually repetitive drudgery and may often constitute the majority of the
work when writing your tests. It's therefore desirable to centralize this work
in a fixture setup function. Tests using the same fixture can then be grouped
together and obtain their fixture from this common setup function.

You may also need to clean up, or "teardown", your test fixture after testing.
Since PHP is garbage collected this is usually unnecessary, but if you're
working with external resources -- opening a file handle, setting a global
configuration variable, etc. -- you need to do some clean up.

Fixture can be managed at different levels of "granularity". Most of the time
you want to recreate it from scratch for each test. This is to ensure, as much
as possible, the outcome of each test depends only on its fixture and not on
other tests or external phenomena, a concept often called "test isolation".
In practice, creating entirely new fixture for each test isn't always possible
or even, at times, desirable. In these cases, we want to be able to manage
fixture that is shared among several tests.


## Fixture Functions

EasyTest offers a number of functions to manage your test fixtures. This is
perhaps most clearly laid out with an example:

```php
<?php
// test_fixtures/setup.php

namespace directory;


function setup() {
    echo __FILE__;
}

function teardown() {
    echo __FILE__;
}
```

```php
<?php
// test_fixtures/test.php

namespace file;

use function easytest\fail;
use easytest\Context;


function setup_file() {
    echo __FILE__;
}

function teardown_file() {
    echo __FILE__;
}


function setup() {
    echo __FUNCTION__;
}

function teardown() {
    echo __FUNCTION__;
}


function test_one(Context $context) {
    $context->teardown(function() { echo __FUNCTION__; });
    fail('Execution stops here.');
    echo __FUNCTION__, "\n";
}

function test_two() {
    echo __FUNCTION__;
}


class Test {
    public function __construct() {
        echo __METHOD__;
    }


    function setup_object() {
        echo __METHOD__;
    }

    function teardown_object() {
        echo __METHOD__;
    }


    function setup() {
        echo __METHOD__;
    }

    function teardown() {
        echo __METHOD__;
    }


    function test_one(Context $context) {
        $context->teardown(function() { echo __FUNCTION__; });
        fail('Execution stops here.');
        echo __METHOD__, "\n";
    }

    function test_two() {
        echo __METHOD__;
    }
}
```

Running EasyTest shows the order and frequency with which everything happens:

    $ easytest --verbose

    OOOFOOOOO.OOOFOOOOO.OOO


    OUTPUT: directory\setup
    test_fixtures/setup.php



    OUTPUT: file\setup_file
    test_fixtures/test.php



    OUTPUT: setup for file\test_one
    file\setup



    FAILED: file\test_one
    Execution stops here.

    in test_fixtures/test.php on line 30



    OUTPUT: file\test_one
    file\{closure}



    OUTPUT: teardown for file\test_one
    file\teardown



    OUTPUT: setup for file\test_two
    file\setup



    OUTPUT: file\test_two
    file\test_two



    OUTPUT: teardown for file\test_two
    file\teardown



    OUTPUT: file\Test
    file\Test::__construct



    OUTPUT: file\Test::setup_object
    file\Test::setup_object



    OUTPUT: setup for file\Test::test_one
    file\Test::setup



    FAILED: file\Test::test_one
    Execution stops here.

    in test_fixtures/test.php on line 65



    OUTPUT: file\Test::test_one
    file\{closure}



    OUTPUT: teardown for file\Test::test_one
    file\Test::teardown



    OUTPUT: setup for file\Test::test_two
    file\Test::setup



    OUTPUT: file\Test::test_two
    file\Test::test_two



    OUTPUT: teardown for file\Test::test_two
    file\Test::teardown



    OUTPUT: file\Test::teardown_object
    file\Test::teardown_object



    OUTPUT: file\teardown_file
    test_fixtures/test.php



    OUTPUT: directory\teardown
    test_fixtures/setup.php



    Seconds elapsed: 0.001
    Memory used: 1.253 MB
    Passed: 2, Failed: 2, Output: 19

As you can see, execution of a test stops when an assertion fails or on any
error. Teardown functions run regardless of whether or not a test completes.
Teardown functions are only skipped if a corresponding setup function does not
complete. This could happen because of an error in the setup function or
because `easytest\skip` was called. If a setup function does not complete, the
item being setup (function, class, file, etc.) is skipped.

Of note is the `setup.php` file, which sets up and tears down a directory of
tests. Whenever EasyTest enters a new directory, it looks for this file and,
if found, includes it before any others. It then searches this file for
directory setup and teardown functions. If either of these functions are
found, `setup` is run before continuing to discover the directory and
`teardown` is run just prior to ascending out of the directory. This file may
also include definitions needed for the tests in the current directory and
need not even define directory fixture functions at all.

EasyTest matches fixture functions without regards to case and matches on both
CamelCase and snake\_case. Fixture functions are recognized if their name
begins with the names shown in the example above. Fixture method names must
match exactly, e.g., an object setup method needs to be a case-insensitive
match to either `setup_obect` or `SetupObject`. If multiple setup and/or
teardown functions are ever found, an error is reported and the associated
item is skipped.


## Managing Resources

One of the most straightforward uses of fixture functions is to manage and
cleanup resources that may persist beyond the lifetime of a test.

As a basic example, consider a situation where you'd like to test a function's
output using PHP's output buffering:

```php
function test_buffering() {
    ob_start();
    produce_output();
    easytest\assert_identical('Expected output', ob_get_contents());
    ob_end_clean();
}
```

If the assertion fails, the output buffer is never deleted. Even if you use
`ob_get_clean` to delete the buffer as you get its contents, this does not
guard against errors during the call to `produce_output`.

If this is the only test using an output buffer, we can ensure the buffer is
deleted by using a test-specific teardown function:

```php
function test_buffering(easytest\Context $context) {
    ob_start();
    $context->teardown('ob_end_clean');
    produce_output();
    easytest\assert_identical('Expected output', ob_get_contents());
}
```

If an output buffer is needed by multiple tests, we can move management of the
buffer into separate setup and teardown functions:

```php
function setup() {
    ob_start();
}

function teardown() {
    ob_end_clean();
}

function test_buffering() {
    produce_output();
    easytest\assert_identical('Expected output', ob_get_contents());
}
```


## Providing Fixtures to Tests

You may have noticed that EasyTest's fixture functions form a natural
hierarchy with directories at the top and individual tests at the bottom.
Setup functions higher in the hierarchy can pass state to setup functions
and/or tests lower in the hierarchy by returning an array of arguments. As
EasyTest performs discovery, these arguments are unpacked and automatically
passed to subordinate fixture functions, class constructors, and test
functions, which accept them by adding parameters to their signature.

Subordinate setup functions "intercept" state from higher setup functions.
Whatever these functions return replaces whatever arguments are passed to it.
This is true regardless of whether or not a function explicitly accepts the
arguments provided to it. Functions may add to, remove from, alter or simply
pass through the arguments they receive. If a setup function is not defined at
a particular level in the hierarchy, arguments are passed directly to the next
subordinate setup function, test function or test class.

Arguments are also passed to teardown functions, but these functions never
return arguments, they only clean up the arguments given to them.

Let's consider an example where we wish to share a common database connection
among a directory of tests:

```php
<?php
// setup.php

namespace test\database;

use example\Database;

function setup() {
    $database = new Database();
    $database->createDatabase();
    return [$database];
}

function teardown(Database $database) {
    $database->deleteDatabase();
}
```

In one of our test files, we might have the following:

```php
<?php
// test.php

use function easytest\assert_identical;
use example\Database;

class TestDatabase {
    private $database;

    function __construct(Database $database) {
        $this->database = $database;
    }

    function setup() {
        $this->database->reset();
    }

    function testInsertRecord() {
        $this->database->insertRecord([1, 2]);
        assert_identical([[1, 2]], $this->database->records());
    }

    function testDeleteRecord() {
        $id = $this->database->insertRecord([1, 2]);
        assert_identical([[1, 2]], $this->database->records());

        $this->database->deleteRecord($id);
        assert_identical([], $this->database->records());
    }
}
```

In the above example, since there is no file setup function, the arguments
returned from `test\database\setup` are provided to `TestDatabaseActions`.
Once passed to a constructor, the test fixture is directly accessible from the
test object's shared state. Consequently, object fixture methods never return
or receive parameters. However, you could also write your test using
functions:

```php
<?php
// test.php

namespace test\database\actions;

use function easytest\assert_identical;
use example\Database;

function setup(Database $database) {
    $database->reset();
    return [$database];
}

function test_insert_record(Database $database) {
    $database->insertRecord([1, 2]);
    assert_identical([[1, 2]], $database->records());
}

function test_delete_record(Database $database) {
    $id = $database->insertRecord([1, 2]);
    assert_identical([[1, 2]], $database->records());

    $database->deleteRecord($id);
    assert_identical([], $database->records());
}
```

In the above example, the arguments returned from `test\database\setup` are
provided to `test\database\actions\setup`, which in turn returns arguments
that are provided to each test. If more setup or teardown is needed, you can
add the necessary functions and they will receive the arguments:

```php
<?php
// test.php

namespace test\database\actions;

use function easytest\assert_identical;
use example\Database;


function setup_file(Database $database) {
    $database->loadTestData();
    return [$database];
}

function teardown_file(Database $database) {
    $database->clearTestData();
}


function setup(Database $database) {
    $database->reset();
    return [$database];
}

function test_insert_record(Database $database) {
    $database->insertRecord([1, 2]);
    assert_identical([[1, 2]], $database->records());
}

function test_delete_record(Database $database) {
    $id = $database->insertRecord([1, 2]);
    assert_identical([[1, 2]], $database->records());

    $database->deleteRecord($id);
    assert_identical([], $database->records());
}
```

You could do the same thing if you organized your tests in a class, but in
this case, it might make more sense to use object fixture methods:

```php
<?php
// test.php

use function easytest\assert_identical;
use example\Database;

class TestDatabase {
    private $database;

    function __construct(Database $database) {
        $this->database = $database;
    }


    function setupObject() {
        $this->database->loadTestData();
    }

    function teardownObject() {
        $this->database->clearTestData();
    }

    function setup() {
        $this->database->reset();
    }


    function testInsertRecord() {
        $this->database->insertRecord([1, 2]);
        assert_identical([[1, 2]], $this->database->records());
    }

    function testDeleteRecord() {
        $id = $this->database->insertRecord([1, 2]);
        assert_identical([[1, 2]], $this->database->records());

        $this->database->deleteRecord($id);
        assert_identical([], $this->database->records());
    }
}
```

In the above examples, notice that a setup function's return value replaces
whatever arguments may have existed before it. If you define a setup function,
it **MUST** accept and pass on the arguments it receives if those arguments
are needed at lower levels.

Let's expand on the database example:

```php
<?php
// test_orders.php

namespace test\database\orders;

use function easytest\assert_true;
use example\Database;
use example\OrderManager;
use example\PaymentProcessor;

function setup_file() {
    $processor = new PaymentProcessor();
    $processor->setTestMode();
    return [$processor];
}


function setup(Database $database, PaymentProcessor $processor) {
    return [new OrderManager($database, $processor)];
}


function test(OrderManager $order) {
    $order->placeOrder();
    assert_true($order->wasPlaced());
}
```

The above example results in an error because
`test\database\orders\setup_file` removes the `Database` argument provided by
`test\database\setup` which is needed by `test\database\orders\setup`. A fixed
example:

```php
<?php
// test_orders.php

namespace test\database\orders;

use function easytest\assert_true;
use example\Database;
use example\OrderManager;
use example\PaymentProcessor;

function setup_file(Database $database) {
    $database->loadTestData();

    $processor = new PaymentProcessor();
    $processor->setTestMode();

    return [$database, $processor];
}

function teardown_file(Database $database, PaymentProcessor $processor) {
    $database->clearTestData();
}


function setup(Database $database, PaymentProcessor $processor) {
    $database->reset();
    return [new OrderManager($database, $processor)];
}


function test(OrderManager $order) {
    $order->placeOrder();
    assert_true($order->wasPlaced());
}
```

In both of the above examples, `test\database\orders\setup` uses the
`Database` and `PaymentProcessor` arguments it receives to instantiate and
return an `OrderManager`. The returned `OrderManager` replaces the `Database`
and `PaymentProcessor` arguments and is provided to each test.


## Multiple Parameterized Test Execution

Continuing with the previous example, let's assume we want to support multiple
database and payment processor backends. Client code (in our example,
`OrderManager`) should function identically regardless of the backend. To
ensure this, we'd like to run the same tests against the various database and
payment processor backends we support.

EasyTest supports this by providing a pair of fixture functions not previously
mentioned: `setup_runs` and `teardown_runs`. These functions may be defined in
a test file and/or in a test directory's `setup.php`. `setup_runs` should
return an iterable of arrays, and EasyTest will run subordinate tests once
with each array of arguments. In the hierarchy of fixture functions,
`setup_runs` is run *before* file and directory setup functions and
`teardown_runs` is run *after* file and directory teardown functions, meaning
that directory and file fixture functions are run once for each set of
arguments returned by `setup_runs`.

```php
<?php
// setup.php

namespace test\database;

use example\DatabaseX;
use example\DatabaseY;

function setup_runs() {
    $db1 = new DatabaseX();
    $db1->createDatabase();

    $db2 = new DatabaseY();
    $db2->createDatabase();

    return [
        'database x' => [$db1],
        'database y' => [$db2],
    ];
}

function teardown_runs(array $args) {
    $args['database x'][0]->deleteDatabase();
    $args['database y'][0]->deleteDatabase();
}
```

```php
<?php
// test_orders.php

namespace test\database\orders;

use function easytest\assert_true;
use example\Database;
use example\OrderManager;
use example\PaymentProcessor;
use example\PaymentProcessorA;
use example\PaymentProcessorB;

function setup_runs(Database $database) {
    $database->loadTestData();

    $processor1 = new PaymentProcessorA();
    $processor1->setTestMode();

    $processor2 = new PaymentProcessorB();
    $processor2->setTestMode();

    return [
        'processor a' => [$database, $processor1],
        'processor b' => [$database, $processor2],
    ];
}

function teardown_runs(array $args) {
    // both payment processors use the same database, so only clear it out once
    $database = $args['processor a'][0];
    $database->clearTestData();
}


function setup(Database $database, PaymentProcessor $processor) {
    $database->reset();
    return [new OrderManager($database, $processor)];
}


function test(OrderManager $order) {
    $order->placeOrder();
    assert_true($order->wasPlaced());
}
```

`test` is now run four times using every combination of database and payment
processor. If an error or failure occurs, the failed run is identified using
the keys of the iterable return by `setup_runs`. In this example, a failure of
`test` might be identified as:

    FAILED: test (database x, processor b)

Unlike other teardown fixture functions, EasyTest does not unpack the iterable
returned by `setup_runs` when calling `teardown_runs`. This is because
EasyTest only traverses the iterator once, thus supporting the use of
generators and other non-rewindable iterators. This might be desirable if the
setup for each run is costly in terms of resources.

In the following example, generators are used so that only one database and
one payment processor are created at a time. Because `teardown_runs` would
received an expended generator, directory and file fixtures are used to setup
and teardown the resources used for each run.

```php
<?php
// setup.php

namespace test\database;

use example\Database;
use example\DatabaseX;
use example\DatabaseY;

function setup_runs() {
    $db = new DatabaseX();
    yield 'database x' => [$db];

    $db = new DatabaseY();
    yield 'database y' => [$db];
}

function setup(Database $db) {
    $db->createDatabase();
    return [$db];
}

function teardown(Database $db) {
    $db->deleteDatabase();
}
```

```php
<?php
// test_orders.php

namespace test\database\orders;

use function easytest\assert_true;
use example\Database;
use example\OrderManager;
use example\PaymentProcessor;
use example\PaymentProcessorA;
use example\PaymentProcessorB;

function setup_runs(Database $database) {
    $processor = new PaymentProcessorA();
    yield 'processor a' => [$database, $processor];

    $processor = new PaymentProcessorB();
    yield 'processor b' => [$database, $processor];
}


function setup_file(Database $database, PaymentProcessor $processor) {
    $database->loadTestData();
    $processor->setTestMode();
    return [$database, $processor];
}

function teardown_file(Database $database, PaymentProcessor $processor) {
    $database->clearTestData();
}


function setup(Database $database, PaymentProcessor $processor) {
    $database->reset();
    return [new OrderManager($database, $processor)];
}


function test(OrderManager $order) {
    $order->placeOrder();
    assert_true($order->wasPlaced());
}
