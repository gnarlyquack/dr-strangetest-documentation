<?php declare(strict_types=1);

use example\Email;
use function strangetest\assert_equal;
use function strangetest\assert_throws;

function test_valid_email(): void
{
    $email = Email::fromString('user@example.com');
    assert($email instanceof Email);
}

function test_invalid_email(): void
{
    assert_throws(
        InvalidArgumentException::class,
        function() { Email::fromString('invalid'); }
    );
}

function test_email_as_string(): void
{
    $email = 'user@example.com';
    assert_equal(Email::fromString($email), $email);
}
