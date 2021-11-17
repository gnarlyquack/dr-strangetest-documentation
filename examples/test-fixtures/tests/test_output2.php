<?php declare(strict_types=1);

function produce_output(): void
{
    echo 'Expected output';
    trigger_error('Did I err?');
}

function test_output(strangetest\Context $context): void
{
    ob_start();
    $context->teardown('ob_end_clean');
    produce_output();
    assert('Expected output' === ob_get_contents());
}
