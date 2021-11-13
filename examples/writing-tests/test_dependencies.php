<?php

function test_one(strangetest\Context $context)
{
    $context->set(1);
}

function test_two(strangetest\Context $context)
{
    $actual = $context->requires('test_one');
    strangetest\assert_identical(1, $actual);
}

function test_three(strangetest\Context $context)
{
    $context->set(3);
}

function test_four(strangetest\Context $context)
{
    $state = $context->requires('test_one', 'test_two', 'test_three');
    strangetest\assert_identical(
        ['test_one' => 1, 'test_three' => 3],
        $state
    );
}
