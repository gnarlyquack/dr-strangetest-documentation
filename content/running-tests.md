## Running Tests

Run Dr. Strangetest on the command line:

    $ strangetest

By default, Dr. Strangetest searches the current directory for tests. Typically you
would run Dr. Strangetest from your project's root directory and place your tests in
a file or directory in that directory. If you use Composer, Dr. Strangetest also
tries to load Composer's autoloader so your project is automatically visible
to your test suite.

You can run individual tests or a subset of tests by invoking Dr. Strangetest with
one or more paths to directories or files in your test suite.

This tests the `test_subdir` directory and `test_foo.php` file in the `tests`
directory:

    strangetest tests/test_subdir tests/test_foo.php

To run specific tests within a file, use test specifiers. Function specifiers
let you test individual functions while class specifiers let you test
individual classes and methods.

This tests two functions, `test_one` and `test_two`, in the file
`test_foo.php`:

    strangetest tests/test_foo.php --function=test_one,test_one

Note that function names should be fully qualified.

This tests two classes, `TestFoo` and `TestBar`, in the file `test_foo.php`:

    strangetest tests/test_foo.php --class=TestFoo,TestBar

Note that class names should be fully qualified.

Methods can also be specified. This tests two methods, `testOne` and
`testTwo`, in class `TestFoo` in the file `test_foo.php`:

    strangetest tests/test_foo.php --class=TestFoo::testOne,testTwo

Note that, if multiple classes are listed, method specifiers are associated
only with the last class in the list. So this tests class `TestFoo` and two
methods in class `TestBar`:

    strangetest tests/test_foo.php --class=TestFoo,TestBar::testOne,testTwo

To specify methods in multiple classes, use multiple class specifiers:

    strangetest tests/test_foo.php --class=TestFoo::testOne,testTwo --class=TestBar::testOne,testTwo

You can, of course, specify multiple paths with muliple specifiers for each:

    strangetest tests/test_foo.php --function=test_one,test_two --class=TestFoo::testOne,testTwo tests/test_bar.php --class=TestBar --function=test_three,test_four
