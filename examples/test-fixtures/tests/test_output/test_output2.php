<?php declare(strict_types=1);

namespace test2;
use strangetest;

function test_output(strangetest\Context $context): void
{
    ob_start();
    $context->teardown('ob_end_clean');
    produce_output();
    assert('Expected output' === ob_get_contents());
}
