# Assertions

If a particular test is supposed to produced a particular outcome, assertions
are how you verify that outcome. This chapter details the various ways you can
make assertions in Dr. Strangetest.


## PHP's assert

The simplest way to make an assertion is to use PHP's built-in `assert`
function. The benefit is that you can make any arbitrary assertion in your
tests. The downside is that PHP typically provides limited information when an
assertion fails. For that reason, you may prefer to use one of [Dr.
Strangetest's assertions](@#dr-strangetests-assertions) or [write your
own](@#writing-custom-assertions).

The behavior of PHP's built-in `assert` function has changed a fair bit over
the various versions of PHP, making consistent, backwards-compatible use
difficult. An overview of these changes and some recommendations are provided
here.

```php
assert(mixed $assertion, string|Throwable $description = null): bool
```

`$assertion` is an expression to be tested by `assert`. The assertion passes if
the expression is truthy, otherwise it fails.

`$description` should explain why the assertion failed and is included in the
test report if the assertion fails. This parameter was added in PHP 5.4.8.


Although `assert` technically returns a boolean, Dr. Strangetest configures
PHP's assertion behavior so that a failed assertion causes an exception to be
thrown. In PHP 7 and higher, this exception is an instance of `AssertionError`,
and in PHP 5, it's an instance of `strangetest\Failure`.

Although `$assertion` can be any expression, PHP 5 and 7 treat strings
specially: the string is evaluated as PHP code, the result of which determines
if the assertion passes. This behavior was deprecated in PHP 7.2 and removed in
PHP 8. In PHP 5, you might prefer using a string for `$assertion`, otherwise
the expression will not be displayed if the assertion fails.

In PHP 7 and higher, if the `assert.exception` configuration option is enabled
and `$description` is an instance of an exception, the exception is thrown if
the assertion fails. Dr. Strangetest supports this, but unless the exception is
an instance of `AssertionError`, the test result is reported as an error
instead of a failure. If `assert.exception` is disabled, the exception is
instead converted to a string and used as the failure message.


## Dr. Strangetest's Assertions

Dr. Strangetest provides the following assertions. These assertions may give
better diagnostics than PHP's `assert` when they fail, but of course, the
assertions you can make are limited to what is listed here. You can always
[write your own](@#writing-custom-assertions) if you need custom behavior.

All assertions behave similarly: if the condition that an individual assertion
is supposed to check is met, the assertion passes. Otherwise, an exception is
thrown signalling an assertion failure. Unless otherwise noted, each assertion
takes an optional `$description` argument that is included in the test report
if the assertion fails.


### assert_different

```php
strangetest\assert_different(
    mixed $expected,
    mixed $actual,
    string $description = null
): void
```

Passes if `$expected !== $actual`.


### assert_equal

```php
strangetest\assert_equal(
    mixed $expected,
    mixed $actual,
    string $description = null
): void
```

Passes if `$expected == $actual`.


### assert_false

```php
strangetest\assert_false(mixed $actual, string $description = null): void
```

Passes if `$actual === false`.


### assert_falsy

```php
strangetest\assert_falsy(mixed $actual, string $description = null): void
```

Passes if `$actual == false`.


### assert_greater

```php
strangetest\assert_greater(
    mixed $actual,
    mixed $min,
    string $description = null
): void
```

Passes if `$actual > $min`.


### assert_greater_or_equal

```php
strangetest\assert_greater_or_equal(
    mixed $actual,
    mixed $min,
    string $description = null
): void
```

Passes if `$actual >= $min`.


### assert_identical

```php
strangetest\assert_identical(
    mixed $expected,
    mixed $actual,
    string $description = null
): void
```

Passes if `$expected === $actual`.


### assert_less

```php
strangetest\assert_less(
    mixed $actual,
    mixed $max,
    string $description = null
): void
```

Passes if `$actual < $max`.


### assert_less_or_equal

```php
strangetest\assert_less_or_equal(
    mixed $actual,
    mixed $max,
    string $description = null
): void
```

Passes if `$actual <= $max`.


### assert_throws

```php
strangetest\assert_throws(
    string $exception,
    callable $callback,
    string $description = null
): Throwable
```

Passes if invoking `$callable` throws an exception that is an instance of
`$exception`. The exception instance is returned. Any other exception is an
error and is rethrown.

Fails if invoking `$callable` does not throw an exception.


### assert_true

```php
strangetest\assert_true(mixed $actual, string $description = null): void
```

Passes if `$actual === true`.


### assert_truthy

```php
strangetest\assert_truthy(mixed $actual, string $description = null): void
```

Passes if `$actual == true`.


### assert_unequal

```php
strangetest\assert_unequal(
    mixed $expected,
    mixed $actual,
    string $description = null
): void
```

Passes if `$expected != $actual`.


### fail

```php
strangetest\fail(string $reason): never
```

Unconditionally fail. `$reason` is required.


## Writing Custom Assertions

You may find yourself wanting to write your own assertions if you want
diagnostics for a particular assertion failure that's different than what you
can obtain from PHP's `assert` or Dr. Strangetest's assertions. An assertion is
just a function or a method that, upon failure, throws an instance of
`AssertionError` (in PHP 7 and higher) or `strangetest\Failure` (in PHP 5). You
might also begin the function name with `assert`, but this is optional.

In the simplest case, you might just write a function that wraps PHP's `assert`
or another Dr. Strangetest assertion. In more complex cases, you might
implement your assertion logic manually, which generally boils down to:

1.  **Check if the assertion passes or fails.** This can consist of arbitrarily
    complex logic that ultimately depends on the outcome of an expression. If
    the expression is true, the assertion passes, otherwise it fails. If the
    assertion fails, then:

2.  **Create a failure message.** This is typically the bulk of an assertion's
    work, and is a custom assertion's raison d'être. Dr. Strangetest offers
    functions to help [create informative failure
    messages](@#creating-failure-messages) that are used by the framework
    itself.

3.  **Throw a failure exception.** As previously noted, this exception should
    be an instance of `AssertionError` (in PHP 7 and higher) or
    `strangetest\Failure` (in PHP 5). You can use [`strangetest\fail`](@#fail)
    as a convenience function, which just takes a message and throws an
    appropriate failure exception for the version of PHP being used.


### Creating Failure Messages

Providing informative output about why an assertion failed can greatly increase
an assertion's usefulness. Consequently, it's often worth the effort to create
a good failure message. What's "good", however, may largely depend on context.

The elements and considerations that typically go into a good failure message
include:

-   **Show the expression that failed.** In general, it's probably advisable to
    show the expression as actual PHP code to be maximally explicit about the
    condition that failed. That said, you might find that describing it in
    natural language might be more concise. E.g., `Assertion "in_array($value,
    $array)" failed` versus `Failed asserting value is in array`.

-   **Show how the expected and actual values differ.** You will want to format
    the variables used in the assertion in a user-friendly way. What is most
    "friendly" can be fairly subjective and context-dependent.

    Considering the above `in_array` example, you almost certainly want to show
    the value that was expected to be in the array. Should you also show the
    array? The initial instinct might be "yes!", but if the structure or
    content of the array is known, showing the entire array might be mostly
    extraneous information. The answer might also depend on if it's possible an
    incorrect value might have been added or if you're only concerned about
    whether a value was added or not. The expected size or values of the array
    might also impact how -- or if -- you want it shown.

    It might be tempting to display the values "inline" in the expression, but
    if an expression's input values are relatively unconstrained, this probably
    won't scale well for large and/or composite values. If `$value = 4` and
    `$array = [1, 3, 5]`, it might be convenient to show `Assertion
    "in_array(4, [1, 3, 5])" failed`, but consider the result if looking for a
    url in a list of urls. Inlining can also result in information loss:
    compare what's conveyed by `4 === 3` versus `$expected === $actual` with
    the values of `$expected` and `$actual` shown separately.

    It's possible there may be no one solution that adequately meets all use
    cases. In these situations, it might be best to implement multiple,
    context-specific assertions.

-   **Allow a user-provided string to elaborate on the failure.** Especially if
    a test contains multiple (similar) assertions, it can be helpful to let the
    caller provide an explanatory description that's included in the failure
    message.

Given all these consideration, Dr. Strangetest provides the following functions
to help with generating informative failure messages.


#### Formatting Variables

Although PHP provides several functions to format values as user-readable
strings, they seem to all have tradeoffs in how they handle certain types of
variables -- especially recursive ones -- and their legibility of output. For
this reason, Dr. Strangetest provides a variable-formatting function that you
might prefer over PHP's built-in ones.


```php
strangetest\format_variable(mixed &$variable): string
```

`$variable` is the variable to format. This is received as a reference in order
to detect recursive values.

A human-readable string representation of `$variable` is returned.


#### Generating Diffs

Generating a diff is a common way to show how two values differ, especially if
the values being compared are composite values and/or multi-line strings.
Showing a diff in these situations is useful because the diff will identify the
specific parts of the value that are different.

```php
strangetest\diff(
    mixed &$from,
    mixed &$to,
    string $from_id,
    string $to_id,
    bool $loose = false
): string
```

`$from` and `$to` are the values to compare. These are received as references
to detect recursive values.

`$from_id` and `$to_id` are used in the generated diff to identify `$from` and
`$to`, respectively.

`$loose` determines the type of comparison to use when generating the diff. If
`true`, the diff is generated using loose comparison (`==`), otherwise strict
comparison (`===`) is used.

The return value is the resulting diff formatted as a string.
`strangetest\format_variable` is used to help generate the string.


#### Formatting Messages

If you structure your assertion failure messages as [described
above](@#creating-failure-messages), you might find yourself with various
string components from which you want to compose a failure message. Dr.
Strangetest provides a function to streamline this process.

```php
strangetest\format_failure_message(
    string $assertion,
    string $description = null,
    string $detail = null
): string
```

`$assertion` is used as the first line and should generally be a string
indicating the assertion expression that failed.

`$description`, if provided and not empty, is used on the next line and should
generally provide a context in which the `$assertion` failed.

`$detail`, if provided and not empty, is double-spaced after the previous line
and should generally provide more detailed information about why `$assertion`
failed. You might use this to display the value of variables used within the
assertion expression.

The return value is a string that combines the arguments as described above.


### A Comprehensive Example

As an example of how to implement your own assertion function and use Dr.
Strangetest's message formatting functions, here is a sample implementation of
`assert_identical`:

```php
use function strangetest\diff;
use function strangetest\fail;
use function strangetest\format_failure_message;

function assert_identical(
    mixed $expected,
    mixed $actual,
    string $description = null
): void
{
    if ($expected === $actual)
    {
        return;
    }

    $assertion = 'Assertion "$expected === $actual" failed';
    $detail = diff($expected, $actual, '$expected', '$actual');

    $reason = format_failure_message($assertion, $description, $detail);
    fail($reason);
}
```

Consider the following call to this function:

```php
assert_identical(1, '1', 'I failed? :-(');
```

Since `1 === '1'` is false, the conditional expression and thus the assertion
as a whole fails. We'd like to provide some indication of the assertion that
failed, so we represent the assertion expression as a string:

```php
$assertion = 'Assertion "$expected === $actual" failed';
```

Now we'd like to show why `$expected` and `$actual` aren't identical, and so
we generate a diff between the values. In this case it's rather obvious, and
it might be tempting to just inline the values into the assertion expression
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
as `$from_id` and `$to_id` into `strangetest\diff` to generate the first two
lines of the diff.

Now we stitch together a final message using `$assertion`, `$description`
(which was provided by the caller of the function), and `$detail`.
`strangetest\format_failure_message` tries remove the drudgery in this, since
`$description` may be blank and/or our assertion may be simple enough we don't
want to generate a detail. The resulting `$reason` looks like:

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

If any argument to `strangetest\format_failure_message` is omitted, it's omitted
in the final message.

Finally, we use this message with `strangetest\fail` to signal failure:

```php
strangetest\fail($reason);
```
