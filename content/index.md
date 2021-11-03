# Don't Worry!

Let's test the code:

1.  **Get Dr. Strangetest.** [Downloading the Phar](https://github.com/gnarlyquack/easytest/releases/latest/download/easytest.phar)
    is probably easiest.

2.  **Write our tests.** As long as the name begins with `test`, Dr.
    Strangetest will find it. So we might put tests for [this code](@sample-code)
    in a file named `test_email.php` in a directory named `tests`:

    ```php
    <?php declare(strict_types=1);

    use example\Email;
    use function strangetest\assert_equal;
    use function strangetest\assert_throws;

    function test_email_can_be_created_from_valid_address(): void
    {
        assert(Email::from_string('user@example.com') instanceof Email);
    }

    function test_email_cannot_be_created_from_invalid_address(): void
    {
        assert_throws(
            InvalidArgumentException::class,
            function() { Email::from_string('invalid'); }
        );
    }

    function test_email_can_be_used_as_a_string(): void
    {
        assert_equal(
            'user@example.com',
            Email::from_string('user@example.com')
        );
    }
    ```

3.  **Test the code.** The output could look something like:

    ```
    $ php strangetest.phar
    Dr. Strangetest

    ...


    Seconds elapsed: 0.004
    Memory used: 1.844 MB
    Passed: 3
    ```

    Dr. Strangetest automatically looks for and includes Composer's
    `autoload.php`, but using Composer isn't required. We can also manually
    include our application's bootstrap file and/or register an autoloader in
    the test suite.

**Achievement unlocked:** quick start completed! This might get you a ways, but
if you're curious what else Dr. Strangetest can do for you, you could do worse
than [peruse the documentation](@documentation).
