- [Custom Assertion Functions](#custom-assertion-functions)
- [A Comprehensive Example](#a-comprehensive-example)
- [Please Contribute!](#please-contribute)


# Custom Assertion Functions

An assertion is just a function (or a method) that, upon failure, throws an
instance of `easytest\Failure` or, in PHP 7, an instance of `AssertionError`.
You might also begin the function name with `assert`, but this is optional.

In the simplest case, you may just want to write a function that wraps PHP's
`assert()` or another EasyTest assertion.

In more complex cases, you can implement your assertion logic manually, which
generally boils down to:

1. Check if the assertion passes or fails. This can consist of arbitrarily
   complex logic that ultimately depends on the outcome of a conditional. If
   the condition is true, the assertion passes, otherwise it fails. If the
   assertion fails, then:
2. Create a failure message. EasyTest offers some functions (described in the
   [README](https://github.com/gnarlyquack/easytest)) to help with creating
   informative failure messages. There is no requirement to use them, but they
   are used by EasyTest itself and provided as part of the framework.
3. Throw a failure exception. EasyTest provides `easytest\fail()`, which just
   takes a failure message and throws a failure exception. The exception it
   throws is compatible with EasyTest regardless of the version of PHP in use.


# A Comprehensive Example

Here is an implementation of `assert_identical`:

```php
function assert_identical($expected, $actual, $msg = null) {
    if ($expected === $actual) {
        return;
    }

    $assertion = 'Assertion "$expected === $actual" failed';

    $expected = easytest\format_variable($expected);
    $actual = easytest\format_variable($actual);
    $detail = easytest\diff($expected, $actual, '$expected', '$actual');

    $reason = easytest\format_failure_message($assertion, $msg, $detail);
    easytest\fail($reason);
}
```

Now let's consider the following call to the above function:

```php
assert_identical(1, '1', 'I failed? :-(');
```

Since `1 === '1'` is false, the conditional check and thus the assertion as a
whole fails. We'd like to provide some indication of the assertion that
failed, so we represent the assertion expression as a string:

```php
$assertion = 'Assertion "$expected === $actual" failed';
```

Then we replace `$expected` and `$actual` with human-readable string
representations of their values using `easytest\format_variable()` so we can
display them in a user-friendly format. The result is:

```php
$expected = "1";
$actual   = "'1'";
```

Now that `$expected` and `$actual` are strings, we use them to generate a diff
showing why they aren't identical. In this case it's rather obvious, and it
might be tempting to just inline the values into the assertion expression
string. However, if multiline strings or composite data types are involved,
showing a diff makes it much easier to determine why the two values differ.
The result is:

```php
$detail = <<<'DIFF'
- $expected
+ $actual

- 1
+ '1'
DIFF;
```

The strings (**not** the variables!) `'$expected'` and `'$actual'` are passed
into `easytest\diff()` to generate the first two lines of the diff.

Now we stitch together a final message using `$assertion`, `$msg`, and
`$detail`.  `easytest\format_failure_message()` tries remove the drudgery in
this, since `$msg` may be blank and/or our assertion may be simple enough we
don't want to generate a detail. The resulting `$reason` looks like:

```php
$reason = <<<'REASON'
Assertion "$expected === $actual" failed
I failed? :-(

- $expected
+ $actual

- 1
+ '1'
REASON;
```

If any argument to `easytest\format_failure_message()` is omitted, it's
omitted in the final message.

Finally, we use this message with `easytest\fail()` to signal failure:

```php
easytest\fail($reason);
```

# Please Contribute!

EasyTest's assertions cover the basics but aren't comprehensive by any means.
If you feel there's an assertion that should really be included with the
framework, please open an issue and (ideally) contribute a pull request!
