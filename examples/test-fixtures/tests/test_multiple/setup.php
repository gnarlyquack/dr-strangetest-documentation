<?php declare(strict_types=1);
// setup.php

namespace test;

require __DIR__ . '/../../src/database.php';

use example\DatabaseX;
use example\DatabaseY;

function setup_run_database_x(): array
{
    $database = new DatabaseX();
    $database->createDatabase();
    return [$database];
}

function teardown_run_database_x(DatabaseX $database): void
{
    $database->deleteDatabase();
}

function setup_run_database_y(): array
{
    $database = new DatabaseY();
    $database->createDatabase();
    return [$database];
}

function teardown_run_database_y(DatabaseY $database): void
{
    $database->deleteDatabase();
}
