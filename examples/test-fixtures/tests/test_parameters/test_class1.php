<?php declare(strict_types=1);
// test.php

namespace test1;
use example\Database;
use function strangetest\assert_identical;

class TestDatabase
{
    private Database $database;

    public function __construct(Database $database)
    {
        $this->database = $database;
    }

    public function setup(): void
    {
        $this->database->reset();
    }

    public function testInsertRecord(): void
    {
        $this->database->insertRecord([1, 2]);
        assert_identical([[1, 2]], $this->database->records());
    }

    public function testDeleteRecord(): void
    {
        $id = $this->database->insertRecord([1, 2]);
        assert_identical([[1, 2]], $this->database->records());

        $this->database->deleteRecord($id);
        assert_identical([], $this->database->records());
    }
}
