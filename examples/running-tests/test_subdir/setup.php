<?php declare(strict_types=1);

namespace subdir;

function setup_run1(string $one): array
{
    return [$one, 1];
}

function setup_run2(string $one): array
{
    return [$one, 2];
}
