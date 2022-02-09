# Don't Worry!

Let's test the code.

1.  **Get Dr. Strangetest.** [Downloading the
    Phar](https://github.com/gnarlyquack/dr-strangetest/releases/latest/download/strangetest.phar)
    is probably easiest. You can also use Composer to add Dr. Strangetest to
    your project:

        $ composer require --dev dr-strangetest/dr-strangetest=*

2.  **Write your tests.** As long as the name begins with `test`, Dr.
    Strangetest will find it. So you might put tests for [this
    code](@sample-code) in a file named `test_email.php` in a directory named
    `tests`:

    ```php
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
    ```

3. **Ensure your projected is loaded.** If using Composer, Dr. Strangetest
   automatically does this by loading Composer's autoloader. Otherwise you can
   do this manually: create the file `setup.php` in your test directory and
   load your project's entry point or bootstrap file:

   ```php
   <?php declare(strict_types=1);

   require __DIR__ . '/../src/Email.php';
   ```

4.  **Test the code.** The output could look something like:

    ```
    $ php strangetest.phar
    Dr. Strangetest

    ...


    Seconds elapsed: 0.004
    Memory used: 1.5 MB
    Passed: 3
    ```


**Achievement unlocked:** quick start completed! This might get you a ways, but
if you're curious what else Dr. Strangetest can do for you, you could do worse
than [peruse the documentation](@documentation).
