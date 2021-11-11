<?php declare(strict_types=1);

namespace example;

final class Email
{
    private $email;

    public function __construct(string $email)
    {
        if (false === \filter_var($email, \FILTER_VALIDATE_EMAIL))
        {
            throw new \InvalidArgumentException(
                \sprintf('"%s" is not a valid email address', $email)
            );
        }
        $this->email = $email;
    }

    public function __toString(): string
    {
        return $this->email;
    }
}
