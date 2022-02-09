<?php declare(strict_types=1);
// setup.php

namespace test;

require_once __DIR__ . '/../../src/database.php';

use example\Database;

function setup(): array
{
    $database = new Database();
    $database->createDatabase();
    return [$database];
}

function teardown(Database $database): void
{
    $database->deleteDatabase();
}
