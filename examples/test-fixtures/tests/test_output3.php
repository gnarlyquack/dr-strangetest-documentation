<?php declare(strict_types=1);

function produce_output(): void
{
    echo 'Expected output';
    //trigger_error('Did I err?');
}

function produce_more_output(): void
{
    echo 'More expected output';
    //trigger_error('Did I err again?');
}


function setup(): void
{
    ob_start();
}

function teardown(): void
{
    ob_end_clean();
}

function test_output(): void
{
    produce_output();
    assert('Expected output' === ob_get_contents());
}

function test_more_output(): void
{
    produce_more_output();
    assert('More expected output' === ob_get_contents());
}
