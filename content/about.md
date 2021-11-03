# Features

-   **Friendly to all.** Dr. Strangetest runs on PHP 5.3 - 8.0, has no external
    dependencies, and doesn't require any particular development environment
    (e.g., Composer not required).
-   **Tests are normal functions or classes.** No need to subclass from an
    inheritance hierarchy.
-   **Tests are automatically discovered and run.** If a name begins with
    `test`, Dr. Strangetest considers it a test.
-   **Modular fixtures** let you manage test resources of varying lifecycles
    and parameterize your tests with them. You can also run your tests multiple
    times with varying sets of arguments.
-   **Subtests** let you make multiple assertions in your tests and ensure they
    all run regardless of failure.
-   **Declare dependencies between tests**, and if any prerequisite test fails,
    dependent tests are skipped.
