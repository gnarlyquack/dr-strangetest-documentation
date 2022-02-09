<?php declare(strict_types=1);
// setup.php

namespace test;

require __DIR__ . '/../../src/database.php';

use example\Database;
use example\DatabaseX;
use example\DatabaseY;

function setup_run_database_x(): array
{
    $database = new DatabaseX();
    return [$database];
}

function setup_run_database_y(): array
{
    $database = new DatabaseY();
    return [$database];
}

function setup(Database $database): array
{
    $database->createDatabase();
    return [$database];
}

function teardown(Database $database): void
{
    $database->deleteDatabase();
}
