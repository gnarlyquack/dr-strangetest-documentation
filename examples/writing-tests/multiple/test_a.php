<?php
// test_a.php

namespace a;
use strangetest\Context;

function setup_run_a1(int $dir_arg)
{
    return [$dir_arg, 3];
}

function setup_run_a2(int $dir_arg)
{
    return [$dir_arg, 4];
}

function test_one(int $dir_arg, int $file_arg, Context $context)
{
    $context->set([$dir_arg, $file_arg]);
}

function test_two(int $dir_arg, int $file_arg, Context $context)
{
    $actual = $context->requires(
        'test_one',
        'b\test_one',
        'c\test_one'
    );
    $expected = [
        'test_one' => [$dir_arg, $file_arg],
        'c\test_one' => $dir_arg,
    ];
    assert($expected === $actual);
}
