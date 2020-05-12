- [Fixture Functions](#fixture-functions)
- [Managing Resources](#managing-resources)
- [Providing Fixtures to Tests](#providing-fixtures-to-tests)
- [Multiple Parameterized Test
  Execution](#multiple-parameterized-test-execution)


# Fixture Functions

A test's "fixture" is the initial state of the system under test as well as
its dependencies. Setting this up is usually repetitive drudgery and may often
constitute the majority of the work when writing your tests. It's therefore
desirable to centralize this work in a fixture setup function. Tests using the
same fixture can then be grouped together and obtain their fixture from this
common setup function.

You may also need to clean up, or "teardown", your test fixture after testing.
Since PHP is garbage collected this is usually unnecessary, but if you're
working with external resources -- opening a file handle, setting a global
configuration variable, etc. -- you need to do some clean up.

Fixture can be managed at different levels of "granularity". Most of the time
you want to recreate it from scratch for each test. This is to ensure, as much
as possible, the outcome of each test depends only on its fixture and not on
other tests or external phenomena, a concept often called "test isolation".
In practice, creating entirely new fixture for each test this isn't always
possible or even, at times, desirable. In these cases, we want to be able to
manage fixture that is shared among several tests.

EasyTest offers a number of functions to manage your test fixtures. This is
perhaps most clearly laid out with an example:

```php
<?php
// test_fixtures/setup.php

function setup_directory() {
    echo __FILE__;
}

function teardown_directory() {
    echo __FILE__;
}
```

```php
<?php
// test_fixtures/test.php

function setup_file() {
    echo __FILE__;
}

function teardown_file() {
    echo __FILE__;
}


function setup_function() {
    echo __FUNCTION__;
}

function teardown_function() {
    echo __FUNCTION__;
}


function test_one(easytest\Context $context) {
    $context->teardown(function() { echo __FUNCTION__; });
    easytest\fail('Test execution stops here.');
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


    function test_one(easytest\Context $context) {
        $context->teardown(function() { echo __FUNCTION__; });
        easytest\fail('Test execution stops here.');
        echo __METHOD__, "\n";
    }

    function test_two() {
        echo __METHOD__;
    }
}
```

Running EasyTest shows the order and frequency with which everything happens.

    $ easytest --verbose

    OOOFOOOOO.OOOFOOOOO.OOO


    OUTPUT: setup_directory
    test_fixtures/setup.php



    OUTPUT: setup_file
    test_fixtures/test.php



    OUTPUT: setup_function for test_one
    setup_function



    FAILED: test_one
    Test execution stops here.

    in test_fixtures/test.php on line 24



    OUTPUT: test_one
    {closure}



    OUTPUT: teardown_function for test_one
    teardown_function



    OUTPUT: setup_function for test_two
    setup_function



    OUTPUT: test_two
    test_two



    OUTPUT: teardown_function for test_two
    teardown_function



    OUTPUT: Test
    Test::__construct



    OUTPUT: Test::setup_object
    Test::setup_object



    OUTPUT: setup for Test::test_one
    Test::setup



    FAILED: Test::test_one
    Test execution stops here.

    in test_fixtures/test.php on line 59



    OUTPUT: Test::test_one
    {closure}



    OUTPUT: teardown for Test::test_one
    Test::teardown



    OUTPUT: setup for Test::test_two
    Test::setup



    OUTPUT: Test::test_two
    Test::test_two



    OUTPUT: teardown for Test::test_two
    Test::teardown



    OUTPUT: Test::teardown_object
    Test::teardown_object



    OUTPUT: teardown_file
    test_fixtures/test.php



    OUTPUT: teardown_directory
    test_fixtures/setup.php



    Seconds elapsed: 0.003
    Passed: 2, Failed: 2, Output: 19

As you can see, execution of a test stops when an assertion fails or on any
error. Teardown functions run regardless of whether or not a test completes.
Teardown functions are only skipped if a corresponding setup function does not
complete. This could happen because of an error in the setup function or
because `easytest\skip()` was called. If a setup function does not complete,
the item being setup (function, class, file, etc.) is skipped.

Of note is the `setup.php` file, which sets up and tears down a directory of
tests. Whenever EasyTest enters a new directory, it looks for this file and,
if found, includes it before any others. It then searches this file for
directory setup and teardown functions. If either of these functions are
found, `setup_directory()` is run before continuing to discover the directory
and `teardown_directory()` is run just prior to ascending out of the
directory. This file may also include definitions needed for the tests in the
current directory and need not even define directory fixture functions at all.

Just like tests, EasyTest matches fixture functions without regards to case
and matches on both CamelCase and snake_case. Fixture functions are recognized
if their name begins with the names shown in the example above. Fixture method
names need to match exactly, e.g., an object setup method needs be a
case-insensitive match to either `setup_obect()` or `SetupObject()`. If
multiple setup and/or teardown functions are ever found, an error is reported
and the associated item is skipped.


# Managing Resources

One of the most straightforward uses of fixture functions is to manage and
cleanup resources that may persist beyond the lifetime of a test.

In our [discussion of
output](https://github.com/gnarlyquack/easytest/wiki/Writing-Tests#output), we
showed a flawed example:

```php
function test_buffering() {
    ob_start();
    function_that_produces_output();
    easytest\assert_identical('Expected output', ob_get_contents());
    ob_end_clean();
}
```

If the assertion fails, the output buffer is never deleted. Even if we use
`ob_get_clean()` to delete the buffer as we get its contents, this does not
guard against errors happening during the call to the function under test.

If this is the only test using an output buffer, we can delete the buffer upon
conclusion of the test by using a test-specific teardown function:

```php
function test_buffering(easytest\Context $context) {
    ob_start();
    $context->teardown('ob_end_clean');
    function_that_produces_output();
    easytest\assert_identical('Expected output', ob_get_contents());
}
```

If an output buffer is needed by multiple tests, we can move management of the
buffer into separate setup and teardown functions:

```php
function setup_function() {
    ob_start();
}

function teardown_function() {
    ob_end_clean();
}

function test_buffering(easytest\Context $context) {
    function_that_produces_output();
    easytest\assert_identical('Expected output', ob_get_contents());
}
```


# Providing Fixtures to Tests

You may have noticed that EasyTest's fixture functions form a natural hierarchy
with directories at the top and individual tests at the bottom. Setup functions
higher in the hierarchy can pass state to setup functions and/or tests lower in
the hierarchy by returning an array of arguments. As EasyTest performs
discovery, these arguments are unpacked and automatically passed to subordinate
fixture functions, class constructors, and test functions, which accept them by
adding parameters to their signature.

Subordinate setup functions "intercept" state from higher setup functions.
Whatever these functions return replaces whatever arguments are passed to it.
This is true regardless of whether or not a function explicitly accepts the
arguments provided to it. Functions may add to, remove from, alter or simply
pass through the arguments they receive. If a setup function is not defined at a
particular level in the hierarchy, arguments are passed directly to the next
subordinate setup function, test function or test class.

Arguments are also passed to teardown functions, but these functions never
return arguments, they only clean up the arguments given to them.

Let's consider an example where we wish to share a common database connection
among a directory of tests:

```php
<?php
// setup.php

function setup_directory() {
    $database = new Database();
    $database->createDatabase();
    return [$database];
}
```

In one of our test files, we might have the following:

```php
<?php
// test.php

class TestDatabase {
    private $database;

    function __construct(Database $database) {
        $this->database = $database;
    }

    function setup() {
        $this->database->reset();
    }

    function test_insert_record() {
        $this->database->insertRecord([1, 2]);
        easytest\assert_identical(
            [[1, 2]],
            $this->database->records()
        );
    }

    function test_delete_record() {
        $id = $this->database->insertRecord([1, 2]);
        easytest\assert_identical(
            [[1, 2]],
            $this->database->records()
        );

        $this->database->deleteRecord($id);
        easytest\assert_identical([], $this->database->records());
    }
}
```

Once the test fixture (in this case, Database) is passed to a constructor, the
fixture is directly accessible from the test object's shared state.
Consequently, object fixture methods never return or receive parameters.
However, we could also write our test using functions:

```php
<?php
// test.php

function setup_function(Database $database) {
    $database->reset();
    return [$database];
}

function test_insert_record(Database $database) {
    $database->insertRecord([1, 2]);
    easytest\assert_identical(
        [[1, 2]],
        $database->records()
    );
}

function test_delete_record(Database $database) {
    $id = $database->insertRecord([1, 2]);
    easytest\assert_identical(
        [[1, 2]],
        $database->records()
    );

    $database->deleteRecord($id);
    easytest\assert_identical([], $database->records());
}
```

In these examples, since there is no file setup function, the arguments from
`setup_directory()` are provided directly to `TestDatabase` and
`setup_function()`. If it turns out more setup -- or teardown! -- is needed,
we can add the necessary functions and they will receive the arguments:

```php
<?php
// test.php

function setup_file(Database $database) {
    $database->loadTestData();
    return [$database];
}

function teardown_file(Database $database) {
    $database->clearTestData();
}


class TestDatabase {
    private $database;

    function __construct(Database $database) {
        $this->database = $database;
    }

    function setup() {
        $this->database->reset();
    }

    function test_insert_record() {
        $this->database->insertRecord([1, 2]);
        easytest\assert_identical(
            [[1, 2]],
            $this->database->records()
        );
    }

    function test_delete_record() {
        $id = $this->database->insertRecord([1, 2]);
        easytest\assert_identical(
            [[1, 2]],
            $this->database->records()
        );

        $this->database->deleteRecord($id);
        easytest\assert_identical([], $this->database->records());
    }
}
```

Again, we could write this as:

```php
<?php
// test.php

function setup_file(Database $database) {
    $database->loadTestData();
    return [$database];
}

function teardown_file(Database $database) {
    $database->clearTestData();
}


function setup_function(Database $database) {
    $database->reset();
    return [$database];
}

function test_insert_record(Database $database) {
    $database->insertRecord([1, 2]);
    easytest\assert_identical(
        [[1, 2]],
        $database->records()
    );
}

function test_delete_record(Database $database) {
    $id = $database->insertRecord([1, 2]);
    easytest\assert_identical(
        [[1, 2]],
        $database->records()
    );

    $database->deleteRecord($id);
    easytest\assert_identical([], $database->records());
}
```

A setup function's return value replaces whatever arguments may have existed
before it. If you define a setup function, it **MUST** accept and pass on the
arguments it receives if those arguments are needed at lower levels.

Let's expand on our database example:

```php
<?php
// test_orders.php

function setup_file() {
    $processor = new PaymentProcessor();
    $processor->setTestMode();
    return [$processor];
}


function setup_function(Database $database, PaymentProcessor $processor) {
    return [new OrderManager($database, $processor]);
}


function test(OrderManager $order) {
    $order->placeOrder();
    easytest\assert_true($order->wasPlaced());
}
```

This example results in an error, because `setup_file()` removes the
`Database` argument passed in by `setup_directory()` which `setup_function()`
was expecting. A fixed example:

```php
<?php
// test_orders.php

function setup_file(Database $database) {
    $database->loadTestData();

    $processor = new PaymentProcessor();
    $processor->setTestMode();

    return [$database, $processor];
}

function teardown_file(Database $database, PaymentProcessor $processer) {
    $database->clearTestData();
}


function setup_function(Database $database, PaymentProcessor $processor) {
    $database->reset();
    return [new OrderManager($database, $processor)];
}


function test(OrderManager $order) {
    $order->placeOrder();
    easytest\assert_true($order->wasPlaced());
}
```


# Multiple Parameterized Test Execution

Directory setup functions and file setup functions offer one additional feature:
they may return multiple sets of arguments. EasyTest then runs subordinate
fixture functions and tests once with each set of arguments. In order for
EasyTest to know you're returning multiple sets of arguments instead of just
one, arguments must be returned using the function `easytest\arglists()`, which
takes an iterable of iterables as its only parameter.

Building upon the previous example, let's assume we want to support multiple
database and payment processor backends. Client code (in our example,
`OrderManager`) should function identically regardless of the backend. To
ensure this, we'd like to run the same tests against the various database and
payment processor backends we support.

```php
<?php
// setup.php

function setup_directory() {
    $db1 = new DatabaseX();
    $db1->createDatabase();

    $db2 = new DatabaseY();
    $db2->createDatabase();

    return easytest\arglists([
        'database x' => [$db1],
        'database y' => [$db2],
    ]);
}
```

```php
<?php
// test_orders.php

function setup_file(Database $database) {
    $database->loadTestData();

    $processor1 = new PaymentProcessorA();
    $processor1->setTestMode();

    $processor2 = new PaymentProcessorB();
    $processor2->setTestMode();

    return easytest\arglists([
        'processor a' => [$database, $processor1],
        'processor b' => [$database, $processor2],
    ]);
}

function teardown_file(array $arglists) {
    // both processors use the same database, so only clear it out once
    $database = $arglists['processor a'][0];
    $database->clearTestData();
}


function setup_function(Database $database, PaymentProcessor $processor) {
    $database->reset();
    return [new OrderManager($database, $processor)];
}


function test(OrderManager $order) {
    $order->placeOrder();
    easytest\assert_true($order->wasPlaced());
}
```

`test()` is now run four times using every combination of database and payment
processor. If an error or failure occurs, the failed run is identified using
the keys of the array passed to `easytest\arglists()`. In this example, a
failure of `test()` might be identified as:

    FAILED: test (database x, processor b)

There's one important change in this example: arguments are no longer unpacked
for file and directory teardown functions. Since these functions are only
called once per file or directory, the entire collection of arguments is
passed to them. Whatever is passed to `easytest\arglists()` by the setup
function is passed to the teardown function.
