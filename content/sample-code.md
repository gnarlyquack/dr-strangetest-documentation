Here's some sample code you might want to test.

In `src/Email.php`:

```php
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
```

If using Composer, you can autoload the code by putting something like the
following in `composer.json`:

```json
{
    "autoload": {
        "classmap": ["src/"]
    }
}
```

Then create the autoloader:

```shell
$ composer install
```

With this done, you can [test the code](@.).
