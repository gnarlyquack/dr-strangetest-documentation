# Running Tests

## Usage

Run Dr. Strangetest on the command line from your project's root directory:

    strangetest [OPTION]... [PATH]...

`[OPTION]...` is zero or more [options to configure Dr. Strangetest's
behavior](@#options). Some of these may cause Dr. Strangetest to exit early
without running your test suite.

`[PATH]...` allows you to [specify one or more paths](@#specifying-tests) in
which to look for tests. If omitted, this defaults to the current directory.

If you use Composer, Dr. Strangetest tries to load Composer's autoloader so
your project is automatically visible to your test suite.


## Specifying Tests

Dr. Strangetest normally runs [your entire test
suite](@writing-tests#what-is-a-test). However, you can also limit the run to a
subset of tests by using test specifiers.

Note that, depending on your shell, you may need to enclose some of the
commands shown below in quotes to prevent the shell from interpreting certain
characters as operators or other special characters.


### Specifying Paths

If you specify one or more paths within your test suite, Dr. Strangetest will
run every test it discovers in those paths.

If the path is a directory, Dr. Strangetest tests the entire directory. You can
further limit tests within the directory by using [run
specifiers](@#specifying-test-runs).

If the path is a file, Dr. Strangetest tests the entire file. You can further
limit tests within the file using [function
specifiers](@#specifying-functions), [class and method
specifiers](@#specifying-classes-and-methods), and/or [run
specifiers](@#specifying-test-runs).

This tests the `test_subdir` directory and `test_foo.php` file in the `tests`
directory:

    strangetest tests/test_subdir tests/test_foo.php


### Specifying Functions

You can limit tests to one or more functions within a file using function
specifiers. A function specifier must follow a file path and is written as
follows:

    --function=NAME...

Function names must be fully qualified. Multiple functions can be specified by
separating them with a comma or by using multiple function specifiers.

This tests two functions, `test_one` and `test_two`, in the file `test.php`:

    strangetest test.php --function=test_one,test_two

This does the same thing:

    strangetest test.php --function=test_one --function=test_two


### Specifying Classes and Methods

You can limit tests to one or more classes or methods within a file by using
class specifiers. A class specifier must follow a file path and is written as
follows:

    --class=CLASSNAME[::METHODNAME...]...

Class names should be fully qualified. Multiple class names can be specified by
separating them with a semicolon or by using multiple class specifiers.

This tests two classes, `TestFoo` and `TestBar`, in the file `test.php`:

    strangetest test.php --class='TestFoo;TestBar'

This does the same thing:

    strangetest test.php --class=TestFoo --class=TestBar

You can also specify individual methods within a class by following the class
name with double colons (`::`) and listing a method name. Multiple methods can
be specified by separating them with a comma.

This tests two methods, `testOne` and `testTwo`, in classes `TestFoo` and
`TestBar` in the file `test.php`:

    strangetest test.php \
        --class='TestFoo::testOne,testTwo;TestBar::testOne,testTwo'


### Specifying Test Runs

You can limit tests to one or more [test
runs](test-fixtures#run-setup-and-teardown) within a file or directory by using
run specifiers. A run specifier must follow a file or directory path and is
written as follows:

    --run=NAME...

Multiple runs can be specified by separating them with a semicolon or by using
multiple run specifiers.

If your test suite defines a hierarchy of runs, you can specify a specific run
by listing each name in the hierarachy separated with a comma. Run names are
matched by the order in which they're listed against decreasing levels of the
declared run hierarchy. If a name is not matched to a particular level in the
hierarchy, all runs at that level are included and the name is checked against
the next lower level of the hierarchy. You can also explicitly include all runs
at a certain level in the hierachy by using an asterisk, `*`.

Consider the following declaration of test runs:

```php
<?php declare(strict_types=1);
// tests/setup.php

function setup_run_one(): array
{
    return ['one'];
}

function setup_run_two(): array
{
    return ['two'];
}
```
```php
<?php declare(strict_types=1);
// tests/test_subdir/setup.php

namespace subdir;

function setup_run1(string $one): array
{
    return [$one, 1];
}

function setup_run2(string $one): array
{
    return [$one, 2];
}
```
```php
<?php declare(strict_types=1);
// tests/test_subdir/test.php

namespace subdir;
use strangetest;

function setup_run_one(string $one, int $two): array
{
    return [$one, $two, $one . $two];
}

function setup_run_two(string $one, int $two): array
{
    return [$one, $two, $two . $one];
}

/*
tests defined here
*/
```

This defines 8 test runs for the file `tests/test_subdir/test.php`:

1. `(one,1,one)`
2. `(one,1,two)`
3. `(one,2,one)`
4. `(one,2,two)`
5. `(two,1,one)`
6. `(two,1,two)`
7. `(two,2,one)`
8. `(two,2,two)`

This executes run 4 for all tests in the file:

    $ strangetest tests/test_subdir/test.php --run=one,2,two

This executes run 6:

    $ strangetest tests/test_subdir/test.php --run=two,1,two

This executes both runs:

    $ strangetest tests/test_subdir/test.php --run='one,2,two;two,1,two'

As does this:

    $ strangetest tests/test_subdir/test.php --run=one,2,two --run=two,1,two

This executes runs 1-4:

    $ strangetest tests/test_subdir/test.php --run=one

This executes runs 3, 4, 7, and 8:

    $ strangetest tests/test_subdir/test.php --run=*,2

The asterisk indicates that all runs from the first level of the hierarchy
(i.e., runs `(one,*)` and `(two,*)`) should be executed. However, since `2`
does not match any runs in the first level of the hierarchy, the asterisk can
be omitted:

    $ strangetest tests/test_subdir/test.php --run=2

The asterisk is necessary if you want to only execute runs 2, 4, 6, and 8, as
run name `two` would otherwise be matched against the first level:

    $ strangetest tests/test_subdir/test.php --run=*,two

The asterisk explicitly executes all runs from the first level of the
hierarchy. Since `two` does not match any runs in the second level of the
hierarchy, all runs from the second level are also executed. Finally, run `two`
is matched in the third level of the hierarchy, and only that run is executed.
Of course, the runs from the second level can be explicitly executed by using
another asterisk:

    $ strangetest tests/test_subdir/test.php --run=*,*,two


### Combining Specifiers

You can combine multiple specifiers to run an assorted selection of tests:

    strangetest \
        tests/test_subdir \
        tests/test_foo.php \
            --function=test_one,test_two \
            --class=TestFoo::testOne,testTwo \
        tests/test_bar.php \
            --run=one \
            --class=TestBar \
        tests/test_bar.php \
            --run=two \
            --function=test_three,test_four

This results in the following tests being run:

-   All tests in the directory `tests/test_subdir`.

-   Functions `test_one` and `test_two` and methods `TestFoo::testOne` and
    `TestFoo::testTwo` in the file `tests/test_foo.php`.

-   Run `one` for all tests in class `TestBar` in the file
    `tests/test_bar.php`.

-   Run `two` for functions `test_three` and `test_four` in the file
    `tests/test_bar.php`.

## Options

Dr. Strangetest understands the following options:

-   `--help`

    Display usage and help information and exit.

-   `-q`, `--quiet`

    Omit reporting skipped tests and output unless they occurred in conjunction
    with an error or failed test. This is the default.

-   `-v`, `--verbose`

    Include skipped tests and all output in reporting.

-   `--version`

    Display the version of Dr. Strangetest in use and exit.


## Configuring PHP

Dr. Strangetest automatically configures PHP to catch any errors in your code
and ensure the framework runs properly. Although nothing prevents you from
overriding these settings, it's strongly recommended that you use what's
described below.


### Errors

All errors are enabled and an error handler is registered that converts all
errors to an `ErrorException` and throws them.


### Assertions

Dr. Strangetest configures PHP's assertions to support using PHP's built-in
`assert` function. [Dr. Strangetest's
assertions](@assertions#dr-strangetests-assertions) do not use `assert`, but
the framework does require `zend.assertion` to be enabled.

`assert_options` is configured as follows:

-   `assert.active` is enabled.
-   `assert.warning` is disabled.
-   `assert.bail` is disabled.
-   `assert.quiet_eval` is disabled.
-   An assertion handler is registered with `assert.callback` that converts all
    failed assertions to an `AssertionError` exception (or a
    `strangetest\Failure` exception in PHP 5) and throws them. These exceptions
    are recognized as failed assertions while any other exception is treated as
    an error. The handler is only called if `assert.exception` is disabled.

In PHP 7 and higher, the following additional configuration occurs:

-   If `zend.assertions` is set to `-1` ("production mode"), Dr. Strangetest
    exits.  Otherwise, this setting is enabled.
-   In PHP 7.2 and higher, `assert.exception` is enabled.
