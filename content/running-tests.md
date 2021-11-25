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

If the path is a directory, Dr. Strangetest tests the entire directory.

If the path is a file, Dr. Strangetest tests the entire file. You can further
limit tests within the file using [function specifiers](@#specifying-functions)
and/or [class and method specifiers](@#specifying-classes-and-methods).

This tests the `test_subdir` directory and `test_foo.php` file in the `tests`
directory:

    strangetest tests/test_subdir tests/test_foo.php


### Specifying Functions

You can limit tests to one or more functions within a file using function
specifiers. A function specifier must follow a file path and are written as
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
class specifiers. A class specifier must follow a file path and are written as
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


### Combining Specifiers

You can, of course, specify multiple paths each with its own specifiers:

    strangetest \
        tests/test_subdir \
        tests/test_foo.php \
            --function=test_one,test_two \
            --class=TestFoo::testOne,testTwo \
        tests/test_bar.php \
            --class=TestBar \
            --function=test_three,test_four


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
changing these settings, it's strongly recommended that you use what's
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
    failed assertions to an `AssertionError` exception (in PHP 7 and higher) or
    a `strangetest\Failure` exception (in PHP 5) and throws them. These
    exceptions are recognized as failed assertions while any other exception is
    treated as an error. The handler is only called if `assert.exception` is
    disabled.

In PHP 7 and higher, the following additional configuration occurs:

-   If `zend.assertions` is set to `-1` ("production mode"), Dr. Strangetest
    exits.  Otherwise, this setting is enabled.
-   In PHP 7.2 and higher, `assert.exception` is enabled.
