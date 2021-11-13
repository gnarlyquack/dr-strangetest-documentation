<?php
// tests/test_hello.php

use example\greet\Hello;
use function strangetest\assert_identical;

class TestHello
{
    public function TestHelloToTheWorld()
    {
        $hello = new Hello;
        assert_identical('Hello, world!', $hello->greet());
    }

    public function TestHelloToHumans()
    {
        $hello = new Hello;
        assert_identical('Hello, human!', $hello->greet('human'));
    }
}
