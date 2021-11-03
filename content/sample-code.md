Here's some sample code that we might want to test.

In `src/Email.php`:

```php
<?php declare(strict_types=1);

namespace example;

final class Email
{
    public static function from_string(string $email): self
    {
        if (self::is_valid_email($email))
        {
            return new self($email);
        }
        else
        {
            throw new \InvalidArgumentException(
                \sprintf('"%s" is not a valid email address', $email)
            );
        }
    }

    public function __toString(): string
    {
        return $this->email;
    }

    private $email;

    private function __construct(string $email)
    {
        $this->email = $email;
    }

    private static function is_valid_email(string $email): bool
    {
        return false !== \filter_var($email, \FILTER_VALIDATE_EMAIL);
    }
}
```

If we're using Composer, we can autoload the code by putting something like the
following in `composer.json`:

```json
{
    "autoload": {
        "classmap": [
            "src/"
        ]
    }
}
```

Then create the autoloader:

```shell
$ composer install
```

With this done, we can [test the code](@.).
