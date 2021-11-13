<?php

use example\greet\Hello;

function testHelloToTheWorld()
{
    $hello = new Hello;
    assert('Hello, world!' === $hello->greet());
}
