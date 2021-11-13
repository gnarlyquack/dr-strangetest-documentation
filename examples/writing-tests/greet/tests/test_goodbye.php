<?php
// tests/test_goodbye.php

use example\greet\GoodBye;
use function strangetest\assert_identical;

class TestGoodBye
{
    function TestGoodByeToTheWorld()
    {
        $adieu = new GoodBye;
        assert_identical('Goodbye, cruel world!', $adieu->bid());
    }

    function TestGoodByeToHumans()
    {
        $adieu = new GoodBye;
        assert_identical('Goodbye, human!', $adieu->bid('human'));
    }
}
