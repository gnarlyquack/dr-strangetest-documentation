<?php

function test_skip()
{
    if (version_compare(PHP_VERSION, MAX_VERSION) >= 0)
    {
        strangetest\skip('PHP version must be less than ' . MAX_VERSION);
    }

    // The actual test goes here. This is never reached if the version
    // requirement isn't met.
}


const MAX_VERSION = '7.2';
