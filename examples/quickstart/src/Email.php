<?php declare(strict_types=1);

namespace example;

final class Email
{
    private function __construct(public readonly string $email)
    {
    }

    static public function fromString(string $email): self
    {
        if (false === \filter_var($email, \FILTER_VALIDATE_EMAIL))
        {
            throw new \InvalidArgumentException(
                \sprintf('"%s" is not a valid email address', $email)
            );
        }
        return new self($email);
    }

    public function __toString(): string
    {
        return $this->email;
    }
}
