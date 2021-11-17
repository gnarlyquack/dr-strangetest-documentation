<?php declare(strict_types=1);

function produce_output(): void
{
    echo 'Expected output';
    trigger_error('Did I err?');
}

function test_output(): void
{
    ob_start();
    produce_output();
    assert('Expected output' === ob_get_contents());
    ob_end_clean();
}
