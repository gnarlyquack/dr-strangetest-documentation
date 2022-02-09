<?php declare(strict_types=1);

namespace subdir;
use strangetest;

function setup_run_one(string $one, int $two): array
{
    return [$one, $two, $one . $two];
}

function setup_run_two(string $one, int $two): array
{
    return [$one, $two, $two . $one];
}


function test_one(...$args)
{
    \array_pop($args);
    echo strangetest\format_variable($args);
}

function test_two(...$args)
{
    \array_pop($args);
    echo strangetest\format_variable($args);
}


class TestBar
{
    private $args;

    public function __construct(...$args)
    {
        $this->args = $args;
    }

    function test_one()
    {
        echo strangetest\format_variable($this->args);
    }

    function test_two()
    {
        echo strangetest\format_variable($this->args);
    }
}
