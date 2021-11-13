<?php

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
