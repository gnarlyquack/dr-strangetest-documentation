<?php

use function strangetest\diff;
use function strangetest\fail;
use function strangetest\format_failure_message;

function assert_identical(
    mixed $expected,
    mixed $actual,
    string $description = null
): void
{
    if ($expected === $actual)
    {
        return;
    }

    $assertion = 'Assertion "$expected === $actual" failed';
    $detail = diff($expected, $actual, '$expected', '$actual');

    $reason = format_failure_message($assertion, $description, $detail);
    fail($reason);
}


function test_assert_identical(): void
{
    assert_identical(1, '1', 'I failed? :-(');
}
