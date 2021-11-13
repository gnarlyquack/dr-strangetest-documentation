<?php
// test_c.php

namespace c;
use strangetest\Context;

function test_one(int $dir_arg, Context $context)
{
    $context->set($dir_arg);
}

function test_two(int $dir_arg, Context $context)
{
    $actual = $context->requires(
        'test_one',
        'a\test_one',
        'b\test_one'
    );
    $expected = ['test_one' => $dir_arg];
    assert($expected === $actual);
}
