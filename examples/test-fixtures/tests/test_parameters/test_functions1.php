<?php declare(strict_types=1);
// test.php

namespace test\database;

use example\Database;
use function strangetest\assert_identical;

function setup(Database $database): array
{
    $database->reset();
    return [$database];
}

function test_insert_record(Database $database): void
{
    $database->insertRecord([1, 2]);
    assert_identical([[1, 2]], $database->records());
}

function test_delete_record(Database $database): void
{
    $id = $database->insertRecord([1, 2]);
    assert_identical([[1, 2]], $database->records());

    $database->deleteRecord($id);
    assert_identical([], $database->records());
}
