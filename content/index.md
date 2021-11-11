# Don't Worry!

Let's test the code.

1.  **Get Dr. Strangetest.** [Downloading the
    Phar](https://github.com/gnarlyquack/easytest/releases/latest/download/easytest.phar)
    is probably easiest.

2.  **Write your tests.** As long as the name begins with `test`, Dr.
    Strangetest will find it. So you might put tests for [this
    code](@sample-code) in a file named `test_email.php` in a directory named
    `tests`:

    ```php
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
    ```

3.  **Test the code.** The output could look something like:

    ```
    $ php strangetest.phar
    Dr. Strangetest

    ..


    Seconds elapsed: 0.004
    Memory used: 1.27 MB
    Passed: 2
    ```

    Dr. Strangetest automatically looks for and includes Composer's
    `autoload.php`, but using Composer isn't required. We can also manually
    include our application's bootstrap file and/or register an autoloader in
    the test suite.

**Achievement unlocked:** quick start completed! This might get you a ways, but
if you're curious what else Dr. Strangetest can do for you, you could do worse
than [peruse the documentation](@documentation).
