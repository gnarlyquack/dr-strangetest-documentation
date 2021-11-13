<?php
// test_b.php

namespace b;
use strangetest\Context;

function setup_run_b1(int $dir_arg)
{
    return [$dir_arg, 5];
}

function setup_run_b2(int $dir_arg)
{
    return [$dir_arg, 6];
}

function test_one(int $dir_arg, int $file_arg, Context $context)
{
    assert((1 === $dir_arg) || (5 === $file_arg));
    $context->set([$dir_arg, $file_arg]);
}

function test_two(int $dir_arg, int $file_arg, Context $context)
{
    $actual = $context->requires(
        'test_one',
        'a\test_one',
        'c\test_one'
    );
    $expected = [
        'test_one' => [$dir_arg, $file_arg],
        'c\test_one' => $dir_arg,
    ];
    assert($expected === $actual);
}
