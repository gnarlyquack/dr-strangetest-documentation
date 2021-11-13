<?php
// test_greet.php

use example\greet\GoodBye;
use example\greet\Hello;
use function strangetest\assert_identical;

function test_hello_to_the_world()
{
    $hello = new Hello;
    assert_identical('Hello, world!', $hello->greet());
}

function test_hello_to_humans()
{
    $hello = new Hello;
    assert_identical('Hello, human!', $hello->greet('human'));
}

function test_goodbye_to_the_world()
{
    $adieu = new GoodBye;
    assert_identical('Goodbye, cruel world!', $adieu->bid());
}

function test_goodbye_to_humans()
{
    $adieu = new GoodBye;
    assert_identical('Goodbye, human!', $adieu->bid('human'));
}
