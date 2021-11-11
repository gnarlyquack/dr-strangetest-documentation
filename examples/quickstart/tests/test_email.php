<?php declare(strict_types=1);

use example\Email;
use function strangetest\assert_throws;

function test_valid_email(): void
{
    $email = new Email('user@example.com');
    assert('user@example.com' == $email);
}

function test_invalid_email(): void
{
    assert_throws(
        InvalidArgumentException::class,
        function() { new Email('invalid'); }
    );
}
