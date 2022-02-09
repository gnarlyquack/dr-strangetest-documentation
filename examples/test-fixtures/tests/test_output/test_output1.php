<?php declare(strict_types=1);

namespace test1;

function test_output(): void
{
    ob_start();
    produce_output();
    assert('Expected output' === ob_get_contents());
    ob_end_clean();
}
